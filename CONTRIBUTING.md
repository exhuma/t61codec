# Contributing

Contributions are welcome. The library implements a static encoding table, so
most changes are likely bug-fixes or tooling improvements.

## Getting started

1. Fork the repository and clone your fork.
2. Install [uv](https://docs.astral.sh/uv/).
3. Install the project and its development dependencies:

   ```console
   uv sync
   ```

4. Install the pre-commit hooks:

   ```console
   uv run pre-commit install
   ```

## Running tests

```console
uv run pytest
```

## Code style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and
formatting. The pre-commit hooks enforce these checks automatically. You can
also run them manually:

```console
pre-commit run --all-files
```

## Submitting changes

Please open a pull request with a clear description of what was changed and
why. If you are fixing a bug, include a test that reproduces the original
problem.
