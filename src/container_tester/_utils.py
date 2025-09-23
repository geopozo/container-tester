import pathlib


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
