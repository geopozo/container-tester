"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import logging
import pathlib
import re
import sys
import time

import click
import docker
from docker.errors import BuildError, ContainerError, DockerException, ImageNotFound

from container_tester import _utils, config

# ruff: noqa: T201 allow print in CLI

logger = logging.getLogger(__name__)

try:
    client = docker.from_env()
    client.ping()
except DockerException:
    logger.warning(
        "Docker is not running. Please start the Docker daemon and try again.",
    )
    sys.exit(1)


@click.group(help=("CLI for testing containers."))
def cli():
    """CLI for test containers."""


def _dockerfile_content(os_name: str, commands: list[str]) -> str:
    has_py = pathlib.Path("pyproject.toml").exists()
    has_lock = pathlib.Path("uv.lock").exists()
    dependencies = []
    if has_py:
        dependencies.append("COPY pyproject.toml /app/pyproject.toml")
    if has_lock:
        dependencies.append("COPY uv.lock /app/uv.lock")
    deps = "\n".join(dependencies) if dependencies else "# no pyproject/lock detected"
    cmds = "\n".join(f"RUN {cmd}" for cmd in commands) if commands else ""
    sync_cmd = "uv sync --locked" if has_lock else "uv sync"
    return f"""\
FROM {os_name}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

{deps}

ENV UV_LINK_MODE=copy
ADD . /app

RUN {sync_cmd}
{cmds}
"""


@cli.command()
@click.option("--os-name", default="", help="Base Docker image to initialize from")
@click.option("--name", default="", help="Name for the generated Dockerfile")
@click.option(
    "--path",
    default=".",
    help="Target directory for Dockerfile (default: current)",
)
def generate_file(os_name: str, name: str, path: str) -> None:
    """
    Generate a Dockerfile based on a given base image.

    Args:
        os_name (str): Base Docker image to initialize from (e.g., 'ubuntu:20.04').
        name (str): Custom name for the Dockerfile. If empty, derived from os_name.
        path (str): Directory to create or retrieve Dockerfiles. Defaults to current
            directory.

    """
    if not os_name.strip():
        raise click.BadParameter("The '--os-name' option cannot be empty.")

    if not name:
        name = re.sub(r"[^a-zA-Z0-9]", "", os_name)

    dir_path = _utils.resolve_dir_path(path, mkdir=True)
    df_name = f"Dockerfile.{name}"
    content = _dockerfile_content(os_name, [])  # por ahora no commands

    (dir_path / df_name).write_text(content)
    click.echo(f"'{df_name}' generated.")


@cli.command()
@click.option("--name", default="", help="Tag name for the Docker image (required)")
@click.option(
    "--path",
    default=".",
    help="Directory containing the Dockerfile (default: current)",
)
@click.option(
    "--clean/--no-clean",
    default=False,
    is_flag=True,
    help="Delete Dockerfile after build (use --clean to enable)",
)
def build(name: str, path: str, *, clean: bool) -> None:
    """
    Build a Docker image from a tagged Dockerfile.

    Args:
        name (str): Tag name for the Docker image. Required.
        path (str): Directory containing the Dockerfile. Defaults to current directory.
        clean (bool): Whether to delete the Dockerfile after build. Enabled by default.

    """
    if not name.strip():
        raise click.BadParameter("The '--name' option cannot be empty.")

    image_tag = name
    df_name = f"Dockerfile.{image_tag}"
    start_time = time.time()
    dir_path = _utils.resolve_dir_path(path)

    try:
        client.images.build(
            path=f"{dir_path}",
            dockerfile=df_name,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )

    except BuildError as e:
        click.secho(e.msg, fg="red")
    else:
        secs = time.time() - start_time
        size = client.images.get(image_tag).attrs["Size"] / (1024 * 1024)
        click.echo(
            f"[{image_tag}] \033[94m{size:.1f} MB\033[0m | \033[93m{secs:.1f}s\033[0m",
        )
        if clean:
            (dir_path / df_name).unlink(missing_ok=True)


@cli.command()
@click.option("--name", default="", help="Tag name for the Docker image (required)")
@click.option(
    "--command",
    default="echo 'Container is running'",
    type=str,
    help="Shell command to execute inside the container.",
)
@click.option(
    "--clean/--no-clean",
    default=False,
    is_flag=True,
    help="Delete Docker image after build (use --clean to enable)",
)
def run(
    name: str,
    command: str,
    *,
    clean: bool = True,
) -> None:
    """Something."""
    if not name.strip():
        raise click.BadParameter("The '--name' option cannot be empty.")
    if not command.strip():
        raise click.BadParameter("The '--command' option cannot be empty.")

    image_tag = name

    try:
        output = client.containers.run(
            image_tag,
            command=command,
            name="choreo_base",
            tty=True,
            remove=True,
            stdout=True,
            stderr=True,
        )
    except (ContainerError, ImageNotFound, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)
    else:
        click.echo(output.decode("utf-8", errors="replace"))
        if clean:
            remove_image(image_tag)


def _clean_dangling() -> None:
    try:
        client.images.prune(filters={"dangling": True})
    except DockerException:
        pass


@cli.command()
@click.option(
    "--image",
    help="Tag or ID of the Docker image to remove (e.g., 'myapp:latest').",
    required=True,
)
def remove_image(image: str) -> None:
    """
    Tag or ID of the Docker image to remove (e.g., 'myapp:latest').

    Args:
        image (str): The tag or ID of the Docker image to remove.

    """
    try:
        client.images.remove(image=image, force=True)
        click.secho(f"Image '{image}' removed.", fg="green")
    except ImageNotFound:
        click.secho(f"Image '{image}' not found.", fg="yellow")
    except DockerException as e:
        click.secho(f"Docker error: {e}", fg="red")


@cli.command()
@click.option(
    "--path",
    default=".",
    help="Directory to create or retrieve Dockerfiles (defaults to current directory)",
)
@click.option(
    "--command",
    default="echo 'Container is running'",
    type=str,
    help="Shell command to execute inside the container.",
)
@click.option(
    "--clean/--no-clean",
    default=True,
    is_flag=True,
    help="Enable cleanup after execution (use --no-clean to disable)",
)
def default_config(path: str, command, *, clean: bool) -> None:
    """Execute default config file."""
    if not command.strip():
        raise click.BadParameter("Command cannot be empty.")

    try:
        for cfg in config.cfg_list:
            os_name = cfg["os_name"]
            name = cfg["name"]

            generate_file(os_name, name, path)
            build(name, path, clean=clean)
            run(name, command, clean=clean)
    except (ImageNotFound, BuildError, Exception) as e:
        print(f"ERROR: {e}")
    finally:
        _clean_dangling()
