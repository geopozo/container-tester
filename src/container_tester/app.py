"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import docker
import typer
from docker.errors import (
    APIError,
    BuildError,
    ContainerError,
    DockerException,
    ImageNotFound,
    NotFound,
)

from container_tester import _utils

# ruff: noqa: T201 allow print in CLI

if TYPE_CHECKING:
    from docker import DockerClient
    from docker.models.containers import Container as DockerContainer
    from docker.models.images import Image as DockerImage


class DockerConfig(TypedDict):
    """Type a docker config."""

    image_tag: str
    os_name: str
    os_commands: list[str]
    pkg_manager: str


def docker_client() -> DockerClient:
    """Return a ready Docker client."""
    try:
        client = docker.from_env()
    except DockerException:
        typer.echo(
            "Docker is not running. Please start the Docker daemon and try again.",
            err=True,
        )
        sys.exit(1)
    else:
        return client


def _dockerfile_template(os_name: str, os_commands: list[str]) -> str:
    has_py = Path("pyproject.toml").exists()
    dependencies = []
    if has_py:
        dependencies.append("COPY pyproject.toml /app/pyproject.toml")
    deps = "\n".join(dependencies) if dependencies else "# no pyproject detected"
    cmds = "\n".join(f"RUN {cmd}" for cmd in os_commands) if os_commands else ""
    return f"""\
FROM {os_name}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

{deps}

ADD . /app

{cmds}
"""


def remove_dockerfile(image_tag: str, path: str) -> None:
    """
    Remove a Dockerfile matching the image tag from the given path.

    Args:
        image_tag (str): Tag used to identify the Dockerfile.
        path (str): Directory to search for the Dockerfile.

    """
    df_name = f"Dockerfile.{image_tag}"
    try:
        dir_path = _utils.resolve_dir_path(path)
        (dir_path / df_name).unlink()
    except DockerException as e:
        typer.secho(f"Failed to remove '{df_name}': {e}", fg=typer.colors.RED, err=True)
    except (TypeError, FileNotFoundError, Exception) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)


def remove_image(client: DockerClient, image_tag: str) -> None:
    """
    Remove a Docker image by image-tag.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag used to identify the docker image to remove.

    """
    try:
        client.images.remove(image=image_tag, force=True)
    except ImageNotFound:
        typer.secho(f"Image '{image_tag}' not found.", fg=typer.colors.RED)
    except (APIError, DockerException) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)


def remove_container(client: DockerClient, container_id: str) -> None:
    """
    Remove a Docker container by container_id.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        container_id (str): Container name or ID to remove.

    """
    try:
        containers: list[DockerContainer] = client.containers.list(all=True)

        for container in containers:
            if container.name == container_id:
                container.stop()
                container.remove(force=True)
                break
    except NotFound:
        typer.secho(
            f"Container '{container_id}' not found.",
            fg=typer.colors.YELLOW,
            err=True,
        )
    except APIError as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)


def _remove_dangling(client: DockerClient) -> None:
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


def _image_exists(client: DockerClient, image_tag: str) -> DockerImage:
    try:
        image = client.images.pull(image_tag)
    except (APIError, ImageNotFound, Exception) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    else:
        return image


def generate_dockerfile(
    client: DockerClient,
    os_name: str,
    image_tag: str,
    path: str,
    os_commands: list[str],
) -> dict[str, Any]:
    """
    Generate a Dockerfile for the given OS and name at the specified path.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        os_name (str): Base OS for the Dockerfile.
        image_tag (str): Identifier used in the Dockerfile name.
        path (str): Directory to save the Dockerfile.
        os_commands (list[str]): List of shell commands to include in the Dockerfile.

    Returns:
        A dictionary with the keys 'name', 'full_path', and 'os_name'.
        If the operation fails, returns a dictionary with the key 'stderr'.

    """
    image = _image_exists(client, os_name)

    try:
        dir_path = _utils.resolve_dir_path(path, mkdir=True)
        df_name = f"Dockerfile.{image_tag}"
        content = _dockerfile_template(os_name, os_commands)
        (dir_path / df_name).write_text(content)
    except (OSError, TypeError, ValueError) as e:
        typer.secho(
            f"Failed to generate Dockerfile: {e}",
            fg=typer.colors.RED,
            err=True,
        )
        return {"stderr": f"{type(e).__name__}:\n{e}"}
    else:
        return {
            "name": df_name,
            "full_path": (dir_path / df_name).as_posix(),
            "os_name": image.attrs.get("RepoTags"),
        }


def build_image(
    client: DockerClient,
    image_tag: str,
    path: str,
    *,
    clean: bool = False,
) -> dict[str, Any]:
    """
    Build a Docker image from a tagged Dockerfile and optionally remove it after build.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag for the resulting Docker image.
        path (str): Directory containing the Dockerfile.
        clean (bool, optional): If True, remove the image after building.
            Defaults to False.

    Returns:
        A dictionary with the keys 'name', 'os', 'size' and 'labels'.
        If the operation fails, returns a dictionary with the key 'stderr'.

    """
    try:
        df_name = f"Dockerfile.{image_tag}"
        dir_path = _utils.resolve_dir_path(path)
        image, _ = client.images.build(
            path=f"{dir_path}",
            dockerfile=df_name,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )
    except BuildError as e:
        typer.secho(e.msg, fg=typer.colors.RED, err=True)
        return {"stderr": f"{type(e).__name__}:\n{e.msg}"}
    except (APIError, TypeError) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
        return {"stderr": f"{type(e).__name__}:\n{e}"}
    else:
        size = image.attrs.get("Size", "") / (1024 * 1024)
        config = image.attrs.get("Config", {})

        if clean:
            remove_image(client, image_tag)

        return {
            "name": image_tag,
            "os": {
                "architecture": image.attrs["Architecture"],
                "base": image.attrs["Os"],
            },
            "size": f"{size:.2f} MB",
            "labels": config.get("Labels"),
        }


def run_container(
    client: DockerClient,
    image_tag: str,
    command: str,
    *,
    clean: bool = False,
) -> dict[str, Any]:
    """
    Run a container from a Docker image with the given command.

    Args:
        client (DockerClient): Docker SDK client instance used to
            perform the build.
        image_tag (str): Tag of the image to run.
        command (str): Command to execute inside the container.
        clean (bool, optional): If True, remove the container after execution.
            Defaults to False.

    Returns:
        A dictionary with the keys 'name', 'container_id', 'command',
            'stdout' and 'stderr'.
            If the operation fails, returns a dictionary with the key 'stderr'.

    """
    try:
        timestamp = int(time.time())
        name = f"container_test_{image_tag}_{timestamp}"
        container: DockerContainer = client.containers.run(
            image_tag,
            command=command or 'echo "Container is running"',
            name=name,
            detach=True,
            stdout=True,
            stderr=True,
        )
        container.wait()
    except (ContainerError, ImageNotFound, APIError) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
        return {"stderr": f"{type(e).__name__}:\n{e}"}
    else:
        stdout_logs = container.logs(stdout=True, stderr=False).decode()
        stderr_logs = container.logs(stdout=False, stderr=True).decode()
        config = container.attrs.get("Config", {})

        if clean:
            remove_container(client, name)

        return {
            "name": name,
            "container_id": container.id,
            "command": config.get("Cmd"),
            "stdout": stdout_logs.strip(),
            "stderr": stderr_logs.strip(),
        }


def test_container(
    os_name: str,
    name: str,
    path: str,
    command: str,
    *,
    clean: bool = False,
) -> list[dict[str, Any]]:
    """
    Generate, build, and run a container from provided arguments.

    Args:
        os_name (str): Base OS for the Dockerfile.
        name (str): Identifier for the image and Dockerfile.
        path (str): Directory to store the Dockerfile.
        command (str): Command to execute in the container.
        clean (bool): If True, remove generated artifacts after execution.

    Returns:
        A list of dictionaries with the keys 'dockerfile', 'image', 'container'.
            If the operation fails, returns a empty list'.

    """
    client = docker_client()

    try:
        docker_info = {
            "dockerfile": generate_dockerfile(client, os_name, name, path, []),
            "image": build_image(client, name, path),
            "container": run_container(client, name, command, clean=clean),
        }

        if clean:
            remove_dockerfile(name, path)
            remove_image(client, name)
            _remove_dangling(client)
    except (ImageNotFound, BuildError, Exception) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
        return []
    else:
        return [docker_info]


def run_config(
    path: str,
    config_list: list[DockerConfig],
    command: str,
    *,
    clean: bool = False,
) -> list[dict[str, Any]] | None:
    """
    Generate, build, and run containers from the default config list.

    Args:
        path (str): Directory to store Dockerfiles.
        config_list (list[DockerConfig]): Docker image profiles to generate files from.
        command (str): Command to execute in the container.
        clean (bool, optional): If True, remove generated files and images
            after execution.

    Returns:
        A list of dictionaries with the keys 'dockerfile', 'image', 'container'.
            If the operation fails, returns a empty list'.

    """
    client = docker_client()
    info_list = []

    try:
        typer.echo(f"Container Tests: {len(config_list)}")
        for i, cfg in enumerate(config_list):
            typer.secho(f"Test: {i + 1}/{len(config_list)}")

            os_name = cfg["os_name"]
            image_tag = cfg["image_tag"]
            os_commands = cfg["os_commands"]
            command = command or 'echo "Container is running"'

            docker_info = {
                "dockerfile": generate_dockerfile(
                    client,
                    os_name,
                    image_tag,
                    path,
                    os_commands,
                ),
                "image": build_image(client, image_tag, path),
                "container": run_container(
                    client,
                    image_tag,
                    command,
                    clean=clean,
                ),
            }

            if clean:
                remove_dockerfile(image_tag, path)
                remove_image(client, image_tag)
                remove_image(client, os_name)
                _remove_dangling(client)

            info_list.append(docker_info)

    except (APIError, Exception) as e:
        typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
        return []
    else:
        return info_list
