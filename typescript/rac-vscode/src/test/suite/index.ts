import * as path from "path";
import Mocha from "mocha";
import { glob } from "glob";

// Mocha entry point the VS Code test host calls inside the extension process.
export async function run(): Promise<void> {
  const mocha = new Mocha({ ui: "tdd", color: true, timeout: 60000 });
  const testsRoot = path.resolve(__dirname, "..");
  const files = await glob("**/*.test.js", { cwd: testsRoot });
  for (const file of files) mocha.addFile(path.resolve(testsRoot, file));
  await new Promise<void>((resolve, reject) => {
    mocha.run((failures) =>
      failures > 0 ? reject(new Error(`${failures} test(s) failed.`)) : resolve(),
    );
  });
}
