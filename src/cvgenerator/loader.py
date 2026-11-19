from __future__ import annotations

import sys
from pathlib import Path

import yaml

from cvgenerator.models import CV


def load_cv(path: Path) -> CV:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return CV.model_validate(raw)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m cvgenerator.loader <cv.yaml>", file=sys.stderr)
        sys.exit(2)
    cv = load_cv(Path(sys.argv[1]))
    print(cv.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
