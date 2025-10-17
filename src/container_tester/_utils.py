from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib as toml
from pathlib import Path
from typing import Any, TypedDict

import typer
from rich.table import Table, box


class DockerConfig(TypedDict):
    """Type a docker config."""

    command: str
    os_name: str
    os_commands: list[str]
    pkg_manager: str


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


def load_config() -> dict[str, DockerConfig]:
    file_name = "docker-config.toml"
    user_path = Path(file_name).expanduser()
    default_path = Path(__file__).parent / file_name

    config_path = user_path if user_path.is_file() else default_path

    try:
        with config_path.open("rb") as f:
            return toml.load(f)
    except toml.TOMLDecodeError as e:
        typer.echo(f"Error parsing TOML from {config_path}: {e}", err=True)
        sys.exit(1)
    except OSError as e:
        typer.echo(f"Error reading config file {config_path}: {e}", err=True)
        sys.exit(1)


def format_json(data: Any, *, pretty: bool = False) -> str:
    return json.dumps(data, indent=2 if pretty else None)


def format_table(title: str, data: dict[str, Any], *, pretty: bool = False) -> Table:
    table = Table(
        title=title if pretty else f"{title}:",
        box=box.HEAVY_HEAD if pretty else None,
        title_justify="center" if pretty else "left",
    )
    table.add_column("key", style="cyan" if pretty else None, no_wrap=True)
    table.add_column("value", style="magenta" if pretty else None)

    for key, value in data.items():
        table.add_row(str(key), str(value))

    return table
