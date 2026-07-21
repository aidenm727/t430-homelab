# Aiden Platform Repository Instructions

## Authority and startup

- GitHub is the canonical documentation source, this repository is the canonical Aiden Platform engineering record, and Atlas is the deterministic engineering interface. Follow `docs/architecture/repository.md`, `docs/architecture/knowledge-authority.md`, `docs/architecture/engineering-sessions.md`, and `docs/standards/engineering-collaboration.md`; reference their canonical owners instead of copying them.
- Before engineering work, run `PYTHONDONTWRITEBYTECODE=1 ./atlas bootstrap` from the repository root. Then verify `git branch --show-current`, `git rev-parse HEAD`, and `git status --short --branch`, and read `docs/current-mission.md`.
- Treat branch, commit, status, upstream tracking, mission, and Atlas output as live observations. Do not fetch or mutate refs merely to refresh them without explicit authorization.
- `docs/current-mission.md` owns active mission state. Generated context and conversation do not replace it, and mission state does not itself grant task authority.

## Authority to act

- Review, analysis, diagnosis, inventory, and design authorization are read-only. Do not implement unless the owner explicitly authorizes implementation for the current task.
- Before editing, state the exact authorized path set and scope. Modify only that set. If another path, capability, external target, or decision is needed, stop and request scope expansion.
- Preserve existing user changes. Do not infer authority from a writable sandbox, an approval prompt, a prior task, a generated context package, or a casual discussion of future work.
- Do not read secret or credential values, authentication stores, private keys, tokens, cookies, secret files, shell-history databases, or credential-bearing environment values.
- Do not access protected content or traverse, peel, select, expose, or mutate a protected reference without exact owner authorization.

## Implementation and generated files

- Keep shell network disabled unless the task explicitly authorizes the exact network action and destination.
- Do not stage, commit, push, fetch, pull, merge, rebase, switch or create branches, change refs or remotes, write to external systems, install or change dependencies, change configuration, or perform destructive actions unless the task explicitly authorizes the exact action.
- `docs/aiden-context.md` and `docs/infrastructure-snapshot.md` are generated and owned by `tools/generate-context.py`. Update authorized canonical sources first, then run the registered generator; never edit generated output directly.

## Verification

- Run task-focused tests first when appropriate. The correct full Python suite is `PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`.
- After authorized repository changes, run `PYTHONDONTWRITEBYTECODE=1 ./atlas validate`, `PYTHONDONTWRITEBYTECODE=1 ./atlas missing`, and `PYTHONDONTWRITEBYTECODE=1 ./atlas sync`.
- Run `git diff --check`, inspect the complete diff, verify `git status --short --branch`, and confirm that only authorized paths changed. Report exact commands, results, remaining uncertainty, and whether generated files are synchronized.
