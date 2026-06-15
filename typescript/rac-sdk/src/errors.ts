/**
 * Error hierarchy for the RAC TypeScript client.
 *
 * Every failure the client raises derives from {@link RacError}, so a consumer
 * (e.g. a VS Code extension) can catch the whole family with one `catch`, then
 * narrow to a concrete subclass when it wants to react specifically — for
 * example showing an "install RAC" prompt only for {@link RacNotFoundError}.
 *
 * A *validation failure* is NOT an error here: `rac validate` exits non-zero
 * with a normal JSON result when a file has issues, and the client returns that
 * result. Errors are reserved for "could not run rac and get an answer".
 */

/** Base class for every error the RAC client raises. */
export class RacError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

/** The `rac` binary could not be found or executed (ENOENT). */
export class RacNotFoundError extends RacError {
  constructor(public readonly racPath: string) {
    super(
      `rac binary not found: ${racPath}. Install RAC ` +
        `(pip install requirements-as-code) or set racPath / RAC_BIN.`,
    );
  }
}

/**
 * `rac` ran but exited with a usage/IO error (typically exit code 2) and
 * produced no parseable JSON — e.g. a missing file or an unknown command.
 */
export class RacExecError extends RacError {
  constructor(
    public readonly args: readonly string[],
    public readonly code: number,
    public readonly stderr: string,
  ) {
    super(
      `rac ${args.join(" ")} failed (exit ${code}): ` +
        `${stderr.trim() || "no error output"}`,
    );
  }
}

/** `rac` exited cleanly but its stdout was not the expected JSON. */
export class RacOutputError extends RacError {
  constructor(
    public readonly args: readonly string[],
    public readonly stdout: string,
  ) {
    super(`rac ${args.join(" ")} produced no parseable JSON output`);
  }
}
