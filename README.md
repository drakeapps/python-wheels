# python-wheels

linux/aarch64 wheels for PyPI projects that don't publish them.

DankWeather's images ship for amd64 and arm64, and CI builds arm64 under QEMU
emulation. A dependency with no aarch64 wheel compiles from source there, and
for `arm-pyart` that takes ~30 minutes. This repo builds those wheels once,
natively on GitHub's arm64 runner, and publishes them as GitHub Release assets.

## Building a wheel

Run the **Build aarch64 wheel** workflow (Actions → Build aarch64 wheel → Run
workflow) with:

| Input | Example |
|---|---|
| `project` | `arm-pyart` |
| `version` | `2.2.0` |
| `python` | `3.11` (must match the consuming image's Python) |
| `import_name` | `pyart` |

It downloads the project's sdist from PyPI (checking PyPI's sha256), builds a
`manylinux` wheel with [cibuildwheel](https://cibuildwheel.pypa.io) using the
project's own `[tool.cibuildwheel]` config, imports the package and every
compiled extension in a clean venv, and attaches the wheel to the release
`<project>-<version>`.

Published wheels are immutable. Consumers pin them by hash, so the workflow
refuses to overwrite an asset that already exists. To rebuild one, delete the
asset first and re-lock everything that pins it.

## Using a wheel (uv)

Point the dependency at the release asset for linux/aarch64 only; every other
platform keeps resolving from PyPI:

```toml
[tool.uv.sources]
arm-pyart = [
  { url = "https://github.com/drakeapps/python-wheels/releases/download/arm-pyart-2.2.0/<wheel filename>", marker = "sys_platform == 'linux' and platform_machine == 'aarch64' and python_version == '3.11'" },
]
```

Then `uv lock`. The lock records the asset's sha256.

## Upgrading

A version bump of a project built here is: run the workflow for the new
version, update the URL in the consumer's `pyproject.toml`, and `uv lock`.
Retire an entry once upstream starts publishing aarch64 wheels.
