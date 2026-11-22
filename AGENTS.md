# MiniPro fork branch policy

This repository uses `bench` for all custom development and as its default
branch. Commit and push completed custom work to `origin/bench`, not `main`
or `master`. This repository-specific policy supersedes the parent directory's
instruction to push to `main`.

`master` mirrors the immediate upstream `master` at
https://github.com/whaslbeck/minipro.git. Update it only by fast-forwarding
from upstream; never add our commits or force-push it. Merge upstream changes
into `bench` when appropriate. Do not recreate a custom `main` branch.

Fetch before pushing. Run `make test-bench` for implementation changes;
documentation-only branch-policy edits do not require hardware or test runs.
