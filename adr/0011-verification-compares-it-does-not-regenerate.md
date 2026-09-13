# 11. Verification compares the artifacts, it does not regenerate them

Status: accepted

## Context

`make check` used to run `build` and `render`, then `git diff --exit-code -- build
docs`. Both halves of that were wrong.

Regenerating first destroys the evidence. A hand edit to `docs/layers.md` was
overwritten by `render` and the check then passed, so the one mistake the target
existed to catch was the one it silently repaired. The README's claim that touching
a generated file "fails the next check" was not true.

Asking git answers a different question. `git diff` compares the working tree to the
index, so a correct but uncommitted change to `keymap.py` — source edited, artifacts
regenerated, nothing staged yet — reported a failure. Staleness is a property of the
source and the artifacts. Whether they are committed is a separate matter, and one
that a verification target has no business deciding.

That distinction matters more once anything runs the target automatically. A gate
that cannot tell "you forgot to rebuild" from "you have not committed yet" blocks on
the normal state of a working session.

## Decision

`make check` compares and writes nothing:

```
check:
	python3 gen_vil.py --check
	python3 render.py build/oklahomer.vil --check-output docs/layers.md
	make test
```

`gen_vil.py --check` builds the document in memory and compares it to the committed
`.vil`. `render.py --check-output PATH` renders in memory and compares to `PATH`.
Neither touches the file it is judging. Git is not consulted.

The staleness checks run before the suite so the failure names the stale file
instead of surfacing as a test failure.

## Consequences

- A hand-edited artifact is now reported and survives long enough to be looked at.
- The target is safe to run at any moment, on any working tree, however dirty.
- `make check` no longer regenerates as a side effect. Use `make all` for that.
- The pre-commit hook still inspects the working tree rather than the staged
  snapshot, so staging an artifact without its source can still commit an
  inconsistent pair. `.github/workflows/check.yml` runs the same target on what
  actually landed, and unlike the hook it is cloned with the repository.
