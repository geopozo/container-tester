"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import pathlib
import sys
import time
from typing import TYPE_CHECKING

import click
import docker
from docker.errors import (
    APIError,
    BuildError,
    ContainerError,
    DockerException,
    ImageNotFound,
    NotFound,
)

from container_tester import _utils, config

if TYPE_CHECKING:
    from docker.models import containers

# ruff: noqa: T201 allow print in CLI


def docker_client() -> docker.DockerClient:
    """Return a ready Docker client."""
    try:
        client = docker.from_env()
    except DockerException:
        click.echo(
            "Docker is not running. Please start the Docker daemon and try again.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        return client


def _dockerfile_template(os_name: str, commands: list[str]) -> str:
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


def remove_dockerfile(image_tag: str, path: str = ".") -> None:
    """
    Remove a Dockerfile matching the image tag from the given path.

    Args:
        image_tag (str): Tag used to identify the Dockerfile.
        path (str): Directory to search for the Dockerfile.
            Defaults to current directory.

    """
    try:
        dir_path = _utils.resolve_dir_path(path)
        df_name = f"Dockerfile.{image_tag}"
        (dir_path / df_name).unlink(missing_ok=True)
        click.secho(f"Dockerfile '\033[93m{df_name}\033[0m' removed.")
    except DockerException as e:
        click.secho(f"Failed to remove '{df_name}': {e}", fg="red", file=sys.stderr)
    except (TypeError, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)


def remove_image(client: docker.DockerClient, image_tag: str) -> None:
    """
    Remove a Docker image by image-tag, showing status messages.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag of the image to remove.

    """
    try:
        client.images.remove(image=image_tag, force=True)
        click.secho(f"Image '\033[93m{image_tag}\033[0m' removed.")
    except ImageNotFound:
        click.secho(f"Image '{image_tag}' not found.", fg="yellow", file=sys.stderr)
    except (APIError, DockerException, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)


def remove_container(client: docker.DockerClient, container_id: str) -> None:
    """
    Remove a Docker container by container-name.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        container_id (str): Container name or ID to remove.

    """
    try:
        containers: list[containers.Container] = client.containers.list()
        for container in containers:
            if container.name == container_id:
                container.stop()
                container.remove()
                break
        click.secho(f"Container '\033[93m{container_id}\033[0m' removed.")
    except NotFound:
        click.secho(
            f"Container '{container_id}' not found.",
            fg="yellow",
            file=sys.stderr,
        )
    except APIError as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)


def remove_dangling(client: docker.DockerClient) -> None:
    """
    Remove dangling Docker images to free up space.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.

    """
    try:
        client.images.prune(filters={"dangling": True})
    except DockerException:
        pass


def _image_exists(client: docker.DockerClient, image_tag: str) -> None:
    try:
        client.images.pull(image_tag)
    except (APIError, ImageNotFound, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)
        sys.exit(1)


def generate_file(
    client: docker.DockerClient,
    os_name: str,
    name: str,
    path: str,
) -> None:
    """
    Generate a Dockerfile for the given OS and name at the specified path.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        os_name (str): Base OS for the Dockerfile.
        name (str): Identifier used in the Dockerfile name.
        path (str): Directory to save the Dockerfile.

    """
    _image_exists(client, os_name)
    try:
        dir_path = _utils.resolve_dir_path(path, mkdir=True)
        df_name = f"Dockerfile.{name}"
        content = _dockerfile_template(os_name, [])  # no commands for now

        (dir_path / df_name).write_text(content)
        click.echo(f"\n'\033[93m{df_name}\033[0m' generated.")
    except (OSError, TypeError, ValueError) as e:
        click.secho(
            f"{type(e).__name__}:\nFailed to generate Dockerfile: {e}",
            fg="red",
            file=sys.stderr,
        )


def build_image(
    client: docker.DockerClient,
    image_tag: str,
    path: str,
    *,
    clean: bool = False,
) -> None:
    """
    Build a Docker image from a tagged Dockerfile and optionally remove it after build.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag for the resulting Docker image.
        path (str): Directory containing the Dockerfile.
        clean (bool, optional): If True, remove the image after building.
            Defaults to False.

    """
    df_name = f"Dockerfile.{image_tag}"
    start_time = time.time()

    try:
        dir_path = _utils.resolve_dir_path(path)
        client.images.build(
            path=f"{dir_path}",
            dockerfile=df_name,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )

    except BuildError as e:
        click.secho(e.msg, fg="red", file=sys.stderr)
    except (APIError, TypeError, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)
    else:
        secs = time.time() - start_time
        size = client.images.get(image_tag).attrs["Size"] / (1024 * 1024)
        click.echo(
            f"[{image_tag}] \033[94m{size:.1f} MB\033[0m | \033[93m{secs:.1f}s\033[0m",
        )
        if clean:
            remove_image(client, image_tag)


def run_container(
    client: docker.DockerClient,
    image_tag: str,
    command: str,
    *,
    clean: bool = False,
) -> None:
    """
    Run a container from a Docker image with the given command.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag of the image to run.
        command (str): Command to execute inside the container.
        clean (bool, optional): If True, remove the container after execution.
            Defaults to False.

    """
    try:
        output = client.containers.run(
            image_tag,
            command=command or 'echo "Container is running"',
            name=f"container_test_{image_tag}",
            tty=True,
            remove=clean,
            stdout=True,
            stderr=True,
        )
        click.echo(output.decode("utf-8", errors="replace"))
    except (ContainerError, ImageNotFound, APIError, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)


def test_container(
    os_name: str,
    name: str,
    path: str,
    *,
    command: str = "",
    clean: bool = False,
) -> None:
    """
    Generate, build, and run a container from provided arguments.

    Args:
        os_name (str): Base OS for the Dockerfile.
        name (str): Identifier for the image and Dockerfile.
        path (str): Directory to store the Dockerfile.
        command (str): Command to execute in the container.
        clean (bool): If True, remove generated artifacts after execution.

    """
    client = docker_client()

    try:
        generate_file(client, os_name, name, path)
        build_image(client, name, path)
        run_container(client, name, command, clean=clean)
        remove_dangling(client)

        if clean:
            remove_dockerfile(name)
            remove_image(client, name)
    except (ImageNotFound, BuildError, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)


def run_config(path: str, *, clean: bool = False) -> None:
    """
    Generate, build, and run containers from the default config list.

    Args:
        path (str): Directory to store Dockerfiles.
        clean (bool, optional): If True, remove generated files and images
            after execution.

    """
    client = docker_client()

    try:
        for cfg in config.cfg_list:
            os_name = cfg["os_name"]
            name = cfg["name"]
            command = 'echo "Container is running"'

            generate_file(client, os_name, name, path)
            build_image(client, name, path)
            run_container(client, name, command, clean=clean)

            if clean:
                remove_dockerfile(name)
                remove_image(client, name)
                remove_image(client, os_name)
    except (ImageNotFound, BuildError, Exception) as e:
        click.secho(f"{type(e).__name__}:\n{e}", fg="red", file=sys.stderr)
    finally:
        remove_dangling(client)
