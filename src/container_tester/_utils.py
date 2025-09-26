import json
import pathlib
from typing import Any


class AutoEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "__json__"):
            return o.__json__()
        return super().default(o)


def resolve_dir_path(
    path: str,
    *,
    mkdir: bool = False,
) -> pathlib.Path:
    dir_path = pathlib.Path(path).expanduser()

    if not dir_path.is_absolute():
        dir_path = dir_path.resolve()

    if dir_path.is_dir():
        return dir_path

    if mkdir:
        dir_path.mkdir(parents=True, exist_ok=True)

    return dir_path


def format_json(data: Any, *, pretty: bool = False) -> str:
    return json.dumps(data, indent=2 if pretty else None, cls=AutoEncoder)
