import fs from "node:fs";
import { describe, it } from "node:test";
import { equal } from "node:assert/strict";
import { MessageFormat } from "messageformat";

function main() {
  const testPaths = process.argv.slice(2);
  for (const testPath of testPaths) {
    const testFile = parseTestFile(testPath);
    runTests(testFile);
  }
}

function parseTestFile(testPath) {
  const testContent = fs.readFileSync(testPath, "utf-8");
  const verifyPath = testPath.replace(/.test.json$/, ".verify.json");
  const verifyContent = fs.readFileSync(verifyPath, "utf-8");
  return {
    testFile: JSON.parse(testContent),
    verifyFile: JSON.parse(verifyContent),
  };
}

function runTests({ testFile, verifyFile }) {
  describe(testFile.scenario, () => {
    for (const test of testFile.verifications) {
      const expected = verifyFile.verifications.find(
        (v) => v.label === test.label
      ).verify;

      switch (testFile.testType) {
        case "syntax":
          runSyntaxTest(test, expected);
          break;
        default:
          throw new Error(`Test type "${testFile.testType}" not supported.`);
      }
    }
  });
}

function runSyntaxTest({ label, locale, pattern, inputs }, expected) {
  it(label, () => {
    const mf = new MessageFormat(pattern, locale);
    const result = mf.format(parseInputs(inputs));
    equal(result, expected);
  });
}

function parseInputs(inputs) {
  return inputs;
}

main();
