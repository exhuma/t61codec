# Contributing

## Scope

The library implements a fixed standard (ITU-T T.61, 1988) and is
feature-complete. The project is in **maintenance mode**. Accepted:

- bug fixes (especially deviations from the recommendation),
- support for new Python versions,
- security fixes,
- documentation and tooling improvements.

Feature requests are declined unless a change in Python itself requires one.

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

The golden T.61 reference data lives in `tests/data/t61_golden.tsv`, one
row per mapping, hand-transcribed from ITU-T T.61 (11/1988) and cited
per row. It must never be generated from the codec. To review it, open
the file (or `column -t -s$'\t'` it) and check each row against the cited
table or figure; `tests/golden.py` is only a strict loader.

## Code style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and
formatting. The pre-commit hooks enforce these checks automatically. You can
also run them manually:

```console
uv run pre-commit run --all-files
```

This also runs `mypy` in strict mode (`uv run mypy`).

## Submitting changes

Please open a pull request with a clear description of what was changed and
why. If you are fixing a bug, include a test that reproduces the original
problem.

## Python support policy

CI tests every CPython version that is currently supported. The list is
computed automatically from [endoflife.date](https://endoflife.date/python),
plus the upcoming pre-release (informational only). A monthly scheduled run
detects breakage caused by new Python releases.

`requires-python` is the oldest supported version at release time. It is only
raised when cutting a release; a CI warning signals when it is due. Update the
`Programming Language :: Python :: 3.x` classifiers at the same time.

## Release procedure

1. Bump `version` in `pyproject.toml`, update `CHANGES.rst`, and update the
   classifiers and `requires-python` if needed.
2. Merge to `master`.
3. Tag the release as `vX.Y.Z` and push the tag.
4. CI publishes to PyPI through Trusted Publishing (the job fails if the tag
   does not match the package version).

### One-time setup

Needed only once:

- On PyPI, add a trusted publisher to the project: owner `exhuma`, repository
  `t61codec`, workflow `pythonpackage.yml`, environment `pypi`.
- In the GitHub repository settings, create the `pypi` environment.
