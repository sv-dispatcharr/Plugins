/**
 * normalise.ts — TypeScript channel name normaliser for the Mixed Lang Bundle plugin.
 * Reads a JSON array of channel name strings from stdin, applies normalisation
 * rules, and writes the result array to stdout.
 *
 * Bundled alongside plugin.py so CodeQL detects TypeScript (reported as the
 * "javascript" language) in addition to Python.
 */

import * as readline from "readline";

interface NormalisedEntry {
  original: string;
  normalised: string;
}

function normalise(name: string): string {
  return name
    .trim()
    // Collapse multiple spaces / non-breaking spaces.
    .replace(/[\s\u00A0]+/g, " ")
    // Uppercase common quality suffixes.
    .replace(/\b(hd|fhd|uhd|4k|sd)\b/gi, (m) => m.toUpperCase())
    // Remove trailing punctuation cruft.
    .replace(/[.,;:\-_]+$/, "")
    .trim();
}

async function main(): Promise<void> {
  const rl = readline.createInterface({ input: process.stdin });
  let raw = "";
  for await (const line of rl) raw += line;

  const names: string[] = JSON.parse(raw);
  const result: NormalisedEntry[] = names.map((n) => ({
    original: n,
    normalised: normalise(n),
  }));

  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
}

main().catch((err) => {
  process.stderr.write(String(err) + "\n");
  process.exit(1);
});
