"""Download a project's sdist from PyPI and check it against PyPI's sha256.

Usage: fetch_sdist.py <project> <version> <dest-dir>

Prints the path of the downloaded sdist, and writes `path` and `sha256` to
$GITHUB_OUTPUT when running in Actions.
"""

import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path


def main() -> None:
    project, version, dest = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    with urllib.request.urlopen(f"https://pypi.org/pypi/{project}/{version}/json") as resp:
        release = json.load(resp)

    sdists = [f for f in release["urls"] if f["packagetype"] == "sdist"]
    if not sdists:
        sys.exit(f"{project}=={version} has no sdist on PyPI")
    sdist = sdists[0]

    dest.mkdir(parents=True, exist_ok=True)
    path = dest / sdist["filename"]
    urllib.request.urlretrieve(sdist["url"], path)

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = sdist["digests"]["sha256"]
    if digest != expected:
        sys.exit(f"sha256 mismatch for {path.name}: got {digest}, PyPI says {expected}")

    print(path)
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write(f"path={path}\nsha256={digest}\n")


if __name__ == "__main__":
    main()
