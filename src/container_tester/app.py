"""Run docker with test commands."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer

from container_tester.docker_backend import DockerBackend, DockerContainerInfo

if TYPE_CHECKING:
    from container_tester._utils import DockerConfig


def test_container(
    os_name: str,
    name: str,
    command: str = "",
    os_commands: list[str] | None = None,
    *,
    clean: bool = False,
) -> DockerContainerInfo:
    """
    Generate, build, and run a container from provided arguments.

    Args:
        os_name (str): Base OS for the Dockerfile.
        name (str): Identifier for the image and Dockerfile.
        command (str): Command to execute in the container.
        os_commands (list[str]): List of shell commands to include in the
                Dockerfile.
        clean (bool): If True, remove generated artifacts after execution.

    """
    docker_test = DockerBackend(os_name, os_commands)

    typer.echo(f"{typer.style('Test', fg=typer.colors.GREEN)}: {os_name}")

    docker_test.build(name)
    container = docker_test.run(name, command)

    if clean:
        docker_test.remove_image(name)
        docker_test.remove_container(container.id or "")
        docker_test.remove_dangling()

    return container


def run_config(
    config_list: dict[str, DockerConfig],
    *,
    clean: bool = False,
) -> list[dict[str, Any]]:
    """
    Generate, build, and run containers from the default config list.

    Args:
        config_list (dict[str, DockerConfig]): Docker image profiles to generate
            files from.
        clean (bool, optional): If True, remove generated files and images
            after execution.

    """
    info_list = []

    typer.echo(f"Container Tests: {len(config_list)}")

    for tag, cfg in config_list.items():
        os_name = cfg["os_name"]
        command = cfg["command"]
        os_commands = cfg["os_commands"]

        docker_info = test_container(
            os_name,
            tag,
            command,
            os_commands,
            clean=clean,
        )

        info_list.append(docker_info)

    return info_list
