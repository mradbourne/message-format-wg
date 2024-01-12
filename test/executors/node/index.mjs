import path from "node:path";
import fs from "node:fs";
import { describe, it } from "node:test";

function main() {
  const testPaths = process.argv.slice(2);
  for (const testPath of testPaths) {
    const testFile = parseTestFile(testPath);
    runTests(testFile);
  }
}

function parseTestFile(testPath) {
  const content = fs.readFileSync(testPath, "utf-8");
  return JSON.parse(content);
}

function runTests(testFile) {
  describe(testFile.scenario, () => {
    for (const test of testFile.verifications) {
      runTest(test);
    }
  });
}

function runTest({ label, locale, pattern, inputs }) {
  it(label, () => {});
}

main();
