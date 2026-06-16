import * as path from "path";
import { runTests } from "@vscode/test-electron";

// Downloads a VS Code build and runs the suite with the extension loaded over
// the fixture corpus. Invoked by `npm test`; in CI it runs under xvfb.
async function main(): Promise<void> {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, "../../");
    const extensionTestsPath = path.resolve(__dirname, "./suite/index");
    const workspace = path.resolve(__dirname, "../../fixtures/corpus");
    await runTests({
      extensionDevelopmentPath,
      extensionTestsPath,
      // Open the fixture corpus so `workspaceContains:**/.rac/config.yaml`
      // activates the extension; disable other installed extensions.
      launchArgs: [workspace, "--disable-extensions"],
    });
  } catch (err) {
    console.error("Failed to run extension tests:", err);
    process.exit(1);
  }
}

void main();
