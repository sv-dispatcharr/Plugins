"""
Go Healthcheck — Dispatcharr plugin

Compiles and runs a bundled Go program (probe.go) that concurrently probes
stream endpoints for reachability, returning per-URL latency and status.

Tests CodeQL detection of co-packaged Go alongside Python: both languages
should appear in the scanned-languages list in the workflow output.
"""

import json
import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
GO_SOURCE = os.path.join(PLUGIN_DIR, "probe.go")


def _get_settings():
    try:
        from apps.plugins.models import PluginConfig
        cfg = PluginConfig.objects.get(key="go-healthcheck")
        return cfg.settings or {}
    except Exception:
        return {}


def get_settings_fields():
    return [
        {
            "key": "timeout_ms",
            "label": "Probe Timeout (ms)",
            "type": "number",
            "default": 3000,
            "description": "Maximum time to wait for each endpoint to respond.",
        },
        {
            "key": "max_streams",
            "label": "Max Streams to Probe",
            "type": "number",
            "default": 50,
            "description": "Cap on concurrent probes per run to avoid hammering the network.",
        },
    ]


def get_actions():
    return [
        {
            "key": "probe_all",
            "label": "Probe All Streams",
            "description": "Run the Go health probe against every active stream URL.",
        }
    ]


def run_action(action_key, params=None):
    settings = _get_settings()
    if action_key == "probe_all":
        return _run_probe(settings)
    return {"success": False, "message": f"Unknown action: {action_key}"}


def _collect_urls(max_streams):
    try:
        from apps.channels.models import Stream
        qs = Stream.objects.filter(is_active=True).values_list("url", flat=True)[:max_streams]
        return list(qs)
    except Exception as e:
        logger.warning(f"go-healthcheck: could not collect stream URLs: {e}")
        return []


def _run_probe(settings):
    timeout_ms = int(settings.get("timeout_ms", 3000))
    max_streams = int(settings.get("max_streams", 50))
    urls = _collect_urls(max_streams)

    if not urls:
        return {"success": True, "message": "No active streams found to probe."}

    # Compile the Go binary once into a temp file.
    with tempfile.NamedTemporaryFile(suffix="", delete=False) as tmp:
        binary_path = tmp.name

    try:
        compile_result = subprocess.run(
            ["go", "build", "-o", binary_path, GO_SOURCE],
            capture_output=True, text=True, timeout=30,
        )
        if compile_result.returncode != 0:
            return {"success": False, "message": f"go build failed: {compile_result.stderr.strip()}"}

        payload = json.dumps({"urls": urls, "timeout_ms": timeout_ms})
        probe_result = subprocess.run(
            [binary_path],
            input=payload, capture_output=True, text=True, timeout=timeout_ms / 1000 * len(urls) + 10,
        )
        if probe_result.returncode == 0:
            return {"success": True, "message": probe_result.stdout.strip()}
        return {"success": False, "message": probe_result.stderr.strip() or "Probe binary exited non-zero."}
    except FileNotFoundError:
        return {"success": False, "message": "Go toolchain not found on this system."}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Probe run timed out."}
    except Exception as e:
        logger.exception("go-healthcheck: unexpected error")
        return {"success": False, "message": str(e)}
    finally:
        try:
            os.unlink(binary_path)
        except OSError:
            pass
