#!/usr/bin/env node
/**
 * handler.js — intentionally vulnerable JS HTTP handler for vuln-test-javascript.
 *
 * !! TEST FIXTURE ONLY — intentionally vulnerable code !!
 *
 * Starts a minimal HTTP server so CodeQL can model HTTP request parameters
 * as taint sources and trace them to dangerous sinks.
 *
 * Violations present:
 *   - js/sql-injection        (CVSS 9.8) — req query param concatenated into SQL
 *   - js/command-injection    (CVSS 9.8) — req query param passed to exec()
 *   - js/path-traversal       (CVSS 7.5) — req query param used in fs.readFile
 *   - js/code-injection       (CVSS 9.8) — eval() on req query param
 *   - js/prototype-pollution  (CVSS 9.8) — unsanitised recursive merge of parsed body
 */

"use strict";

const http = require("http");
const url = require("url");
const fs = require("fs");
const { exec } = require("child_process");

const PORT = process.env.PORT || 19876;

http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  const q = parsed.query;

  // js/sql-injection: URL query param concatenated directly into a SQL string.
  const name = q.name || "";
  const sqlString = "SELECT * FROM channels_channel WHERE name = '" + name + "'";

  // js/command-injection: URL query param passed to child_process.exec.
  const cmd = q.cmd || "echo hello";
  exec(cmd, (err, stdout) => {
    // result used below
    const shellOut = err ? err.message : stdout.trim();

    // js/path-traversal: URL query param passed to fs.readFile.
    const filePath = q.file || "/tmp/data.txt";
    fs.readFile(filePath, "utf8", (readErr, fileData) => {
      // js/code-injection: URL query param passed to eval().
      const expression = q.expr || "1+1";
      let evalResult;
      try {
        evalResult = String(eval(expression));
      } catch (e) {
        evalResult = e.message;
      }

      // js/prototype-pollution: recursive object merge without hasOwnProperty guard.
      function merge(target, source) {
        for (const key in source) {
          if (typeof source[key] === "object" && source[key] !== null) {
            if (!target[key]) target[key] = {};
            merge(target[key], source[key]);
          } else {
            target[key] = source[key];
          }
        }
        return target;
      }

      let extra = {};
      try {
        extra = JSON.parse(q.extra || "{}");
      } catch (_) {}
      const merged = merge({}, extra);

      const body = JSON.stringify({
        sql: sqlString,
        shell: shellOut,
        file: readErr ? "(not found)" : (fileData || "").slice(0, 200),
        eval: evalResult,
        merged,
      });

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(body);
    });
  });
}).listen(PORT);

