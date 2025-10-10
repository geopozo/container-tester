"""Run docker with test commands."""

from __future__ import annotations

from typing import Any, TypedDict

import typer

from container_tester.docker_backend import DockerBackend


class DockerConfig(TypedDict):
    """Type a docker config."""

    image_tag: str
    os_name: str
    os_commands: list[str]
    pkg_manager: str


class DockerInfo(TypedDict):
    """Type a docker info."""

    image: dict[str, Any]
    container: dict[str, Any]


def test_container(  # noqa: PLR0913
    os_name: str,
    name: str,
    path: str,
    command: str = "",
    os_commands: list[str] | None = None,
    *,
    clean: bool = False,
) -> DockerInfo:
    """
    Generate, build, and run a container from provided arguments.

    Args:
        os_name (str): Base OS for the Dockerfile.
        name (str): Identifier for the image and Dockerfile.
        path (str): Directory to store the Dockerfile.
        command (str): Command to execute in the container.
        os_commands (list[str]): List of shell commands to include in the
                Dockerfile.
        clean (bool): If True, remove generated artifacts after execution.

    """
    docker_test = DockerBackend(os_name)

    docker_info = DockerInfo(
        image=docker_test.build(path, name, os_commands),
        container=docker_test.run(name, command, clean=clean),
    )

    if clean:
        docker_test.remove_image(name)
        docker_test.remove_dangling()

    return docker_info


def run_config(
    path: str,
    config_list: list[DockerConfig],
    command: str,
    *,
    clean: bool = False,
) -> list[DockerInfo] | None:
    """
    Generate, build, and run containers from the default config list.

    Args:
        path (str): Directory to store Dockerfiles.
        config_list (list[DockerConfig]): Docker image profiles to generate files from.
        command (str): Command to execute in the container.
        clean (bool, optional): If True, remove generated files and images
            after execution.

    Returns:
        A list of DockerInfo.

    """
    info_list = []

    typer.echo(f"Container Tests: {len(config_list)}")
    for i, cfg in enumerate(config_list):
        typer.secho(f"Test: {i + 1}/{len(config_list)}")
        os_name = cfg["os_name"]
        image_tag = cfg["image_tag"]
        os_commands = cfg["os_commands"]
        command = command or 'echo "Container is running"'

        docker_info = test_container(
            os_name,
            image_tag,
            path,
            command,
            os_commands,
            clean=clean,
        )

        info_list.append(docker_info)

    return info_list
