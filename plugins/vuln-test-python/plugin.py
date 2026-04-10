"""
Vuln Test Python — Dispatcharr plugin

!! TEST FIXTURE ONLY — intentionally vulnerable code !!

Contains multiple high/critical CodeQL violations to verify that the
validate-plugin workflow correctly detects, blocks, and reports them.

Violations present:
  - py/sql-injection          (CVSS 9.8) — request.GET param in raw SQL
  - py/command-injection      (CVSS 9.8) — request.POST param to shell subprocess
  - py/code-injection         (CVSS 9.8) — eval() on request.POST param
  - py/path-injection         (CVSS 7.5) — request.GET param used in open()
  - py/unsafe-deserialization (CVSS 9.8) — pickle.loads on request.body
"""

import pickle
import subprocess

from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views import View


class SearchView(View):
    """GET /plugins/vuln-test-python/search?term=<user input>"""

    def get(self, request):
        # py/sql-injection: unsanitised query parameter interpolated into SQL.
        term = request.GET.get("term", "")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM channels_channel WHERE name LIKE '%" + term + "%'"
            )
            rows = cursor.fetchall()

        # py/path-injection: user-controlled path passed to open().
        export_path = request.GET.get("export_path", "/tmp/export.txt")
        with open(export_path, "w") as fh:
            for row in rows:
                fh.write(str(row) + "\n")

        return JsonResponse({"count": len(rows)})


class CommandView(View):
    """POST /plugins/vuln-test-python/run"""

    def post(self, request):
        # py/command-injection: user POST param passed to shell.
        cmd = request.POST.get("cmd", "echo hello")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # py/code-injection: eval() on user-controlled POST param.
        expr = request.POST.get("expr", "1+1")
        value = eval(expr)  # noqa: S307

        # py/unsafe-deserialization: pickle.loads on raw request body.
        if request.content_type == "application/octet-stream":
            obj = pickle.loads(request.body)  # noqa: S301
            return JsonResponse({"obj": str(obj)})

        return JsonResponse({"output": result.stdout.strip(), "value": str(value)})


# ---------------------------------------------------------------------------
# Plugin stub — these are not called by the workflow, only the views above
# ---------------------------------------------------------------------------

def get_settings_fields():
    return []


def get_actions():
    return []


def run_action(action_key, params=None):
    return {"success": False, "message": "Use the HTTP views directly for testing."}

