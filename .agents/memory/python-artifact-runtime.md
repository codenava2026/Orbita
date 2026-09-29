---
name: Python artifact runtime
description: Runtime conventions for Python services embedded in this pnpm workspace.
---

Python services in this workspace can run as artifact services through a pnpm package script, with dependencies managed by the root uv environment. Operational scripts should be invoked with `uv run python -m package.module` from the artifact directory rather than by file path, because direct file execution omits the package root from `sys.path`.

**Why:** The service workflow is managed by the artifact router and starts from the package directory, while the workspace still uses pnpm for orchestration.

**How to apply:** Keep the service command in the artifact package script, use `uv run` for Python commands, and use module execution for scripts that import the application package.