from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib as toml
from pathlib import Path
from typing import Any

# ruff: noqa: T201 allow print in CLI


def get_cwd() -> Path | None:
    git_path = shutil.which("git")

    if not git_path:
        return None

    r = subprocess.run(  # noqa: S603
        [git_path, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    return Path() if r.returncode else Path(r.stdout.strip())


def resolve_dir_path(
    path: str,
    *,
    mkdir: bool = False,
) -> Path:
    try:
        dir_path = Path(path).expanduser()

        if not dir_path.is_absolute():
            dir_path = dir_path.resolve()

        if dir_path.is_dir():
            return dir_path

        if mkdir:
            dir_path.mkdir(parents=True, exist_ok=True)

    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        print(f"{type(e).__name__}:\n{e}", file=sys.stderr)
        sys.exit(1)
    else:
        return dir_path


def load_config() -> list[Any]:
    file_name = "docker-config.toml"
    user_path = Path(file_name).expanduser()
    default_path = Path(__file__).parent / file_name

    config_path = user_path if user_path.is_file() else default_path

    try:
        with config_path.open("rb") as f:
            data = toml.load(f)
            config_list = data.get("docker_configs", {}).get("profile", [])
    except toml.TOMLDecodeError as e:
        print(f"Error parsing TOML from {config_path}: {e}", file=sys.stderr)
    except OSError as e:
        print(f"Error reading config file {config_path}: {e}", file=sys.stderr)
    else:
        return config_list

    return []
