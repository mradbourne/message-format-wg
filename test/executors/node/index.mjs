import path from "node:path";
import fs from "node:fs";
import { describe, it } from "node:test";

const TEST_DIR = path.join("..", "..", "DDT_DATA");

function main() {
  const testPaths = ["foo.test.json"];
  for (const testPath of testPaths) {
    const testFile = parseTestFile(testPath);
    runTests(testFile);
  }
}

function parseTestFile(testPath) {
  const content = fs.readFileSync(path.join(TEST_DIR, testPath), "utf-8");
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
