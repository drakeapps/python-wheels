"""Import a package and every compiled extension module inside it.

Usage: smoke_test.py <import-name>

A wheel whose extensions were built against the wrong ABI, or are missing a
shared library, fails here rather than in a downstream image.
"""

import importlib
import importlib.machinery
import sys
from pathlib import Path


def main() -> None:
    name = sys.argv[1]
    package = importlib.import_module(name)
    root = Path(package.__file__).parent

    # Only the tagged suffixes (.cpython-311-<platform>.so, .abi3.so): a bare
    # .so inside a package is usually a bundled library, not a module.
    suffixes = [s for s in importlib.machinery.EXTENSION_SUFFIXES if s.count(".") > 1]
    extensions = []
    for suffix in suffixes:
        for path in root.rglob(f"*{suffix}"):
            rel = path.relative_to(root.parent)
            extensions.append(".".join(rel.parts)[: -len(suffix)])

    if not extensions:
        sys.exit(f"no compiled extensions found under {root}")

    for module in sorted(set(extensions)):
        importlib.import_module(module)
        print(f"ok  {module}")

    print(f"{name} {getattr(package, '__version__', '?')}: {len(set(extensions))} extension modules import")


if __name__ == "__main__":
    main()
