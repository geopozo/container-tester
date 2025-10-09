from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib as toml
from pathlib import Path
from typing import Any

import typer
from rich.table import Table, box

# ruff: noqa: T201 allow print in CLI


class AutoEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "__json__"):
            return o.__json__()
        return super().default(o)


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
        typer.echo(f"{type(e).__name__}:\n{e}", err=True)
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
            config_list = data.get("docker_config", {}).get("profile", [])
    except toml.TOMLDecodeError as e:
        typer.echo(f"Error parsing TOML from {config_path}: {e}", err=True)
    except OSError as e:
        typer.echo(f"Error reading config file {config_path}: {e}", err=True)
    else:
        return config_list

    return []


def format_json(data: Any, *, pretty: bool = False) -> str:
    return json.dumps(data, indent=2 if pretty else None, cls=AutoEncoder)


def to_table(title: str, data: dict[str, Any], *, pretty: bool = False) -> Table:
    table = Table(
        title=title if pretty else f"{title}:",
        box=box.HEAVY_HEAD if pretty else None,
        title_justify="center" if pretty else "left",
    )
    table.add_column("field", style="cyan" if pretty else None, no_wrap=True)
    table.add_column("value", style="magenta" if pretty else None)

    for key, value in data.items():
        table.add_row(str(key), str(value))

    return table
