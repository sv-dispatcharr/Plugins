#!/usr/bin/env node
/**
 * handler.js — intentionally vulnerable JS handler for vuln-test-javascript.
 *
 * !! TEST FIXTURE ONLY — intentionally vulnerable code !!
 *
 * Violations present:
 *   - js/sql-injection        (CVSS 9.8) — user input concatenated into SQL string
 *   - js/command-injection    (CVSS 9.8) — user input passed to child_process.exec
 *   - js/path-traversal       (CVSS 7.5) — user-controlled path passed to fs.readFile
 *   - js/code-injection       (CVSS 9.8) — eval() on user-controlled string
 *   - js/prototype-pollution  (CVSS 9.8) — unsanitised recursive merge of user object
 */

"use strict";

const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

async function main() {
  let raw = "";
  for await (const chunk of process.stdin) raw += chunk;
  const settings = JSON.parse(raw);

  const results = {};

  // js/sql-injection: user query concatenated directly into a SQL string.
  const query = settings.query || "";
  const sqlString = "SELECT * FROM channels WHERE name = '" + query + "'";
  results.sql = sqlString;

  // js/command-injection: user-supplied string passed to exec as a shell command.
  const shellCmd = settings.shell_cmd || "echo hello";
  await new Promise((resolve) => {
    exec(shellCmd, (err, stdout) => {
      results.shell = err ? err.message : stdout.trim();
      resolve();
    });
  });

  // js/path-traversal: user-supplied path used directly in fs.readFile.
  const filePath = settings.file_path || "/tmp/data.txt";
  try {
    results.file = fs.readFileSync(filePath, "utf8").slice(0, 200);
  } catch {
    results.file = "(not found)";
  }

  // js/code-injection: eval() on user-controlled expression.
  const expression = settings.expression || "1+1";
  try {
    results.eval = String(eval(expression));
  } catch (e) {
    results.eval = e.message;
  }

  // js/prototype-pollution: deep merge without hasOwnProperty guard.
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
  const userPayload = settings.extra || {};
  results.merged = merge({}, userPayload);

  process.stdout.write(JSON.stringify(results, null, 2) + "\n");
}

main().catch((err) => {
  process.stderr.write(err.message + "\n");
  process.exit(1);
});
