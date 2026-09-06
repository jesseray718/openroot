# Contributing to agape-ipfs

Thank you for your interest in contributing.

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `bash test/run_tests.sh`
5. Check syntax: `bash -n bin/agape-ipfs`
6. Commit with conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
7. Push and open a pull request

## Guidelines

- Keep the tool POSIX-friendly where possible. Bash 4+ is acceptable.
- No new runtime dependencies. If it can't be done with bash, curl, python3, and standard Unix tools, it doesn't belong here.
- Every new command must have a corresponding test in `test/run_tests.sh`.
- Security: Never expose tokens in process arguments. Use header files or environment variables.
- Keep the ledger format append-only JSONL. Never modify or delete entries programmatically.

## Code Style

- 2-space indentation in bash
- Functions prefixed with `cmd_` for commands, `pin_` for pin methods
- `log()` for stderr output, `printf`/`echo` for stdout results
- Every function should fit on one screen (\~30 lines max). If longer, split it.

## Reporting Issues

Open a GitHub issue with:

- Your OS and bash version
- The exact command you ran
- The output (redact any tokens)
- What you expected vs. what happened
