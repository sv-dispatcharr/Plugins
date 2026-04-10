#!/usr/bin/env node
/**
 * webhook_handler.js
 * Reads a JSON payload from stdin, signs it with an optional HMAC secret,
 * and POSTs it to the configured URL.
 *
 * Bundled alongside plugin.py so CodeQL will detect JavaScript in this plugin.
 */

const https = require("https");
const http = require("http");
const crypto = require("crypto");

async function main() {
  let raw = "";
  for await (const chunk of process.stdin) raw += chunk;

  const { event, url, secret } = JSON.parse(raw);
  const body = JSON.stringify({ event, timestamp: Date.now() });

  const headers = { "Content-Type": "application/json" };
  if (secret) {
    headers["X-Hub-Signature-256"] =
      "sha256=" + crypto.createHmac("sha256", secret).update(body).digest("hex");
  }

  const parsed = new URL(url);
  const lib = parsed.protocol === "https:" ? https : http;

  await new Promise((resolve, reject) => {
    const req = lib.request(
      { hostname: parsed.hostname, port: parsed.port, path: parsed.pathname + parsed.search, method: "POST", headers },
      (res) => {
        process.stdout.write(`HTTP ${res.statusCode}\n`);
        resolve();
      }
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

main().catch((err) => {
  process.stderr.write(err.message + "\n");
  process.exit(1);
});
