"""Run docker with test commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    docker_test = DockerBackend(
        os_name,
        image_tag=name,
        command=command,
        os_commands=os_commands,
    )

    typer.echo(f"{typer.style('Test', fg=typer.colors.GREEN)}: {os_name}")

    docker_test.build()
    container = docker_test.run()

    if clean:
        docker_test.remove_image()
        docker_test.remove_container(container.id or "")
        docker_test.remove_dangling()

    return container


def run_config(
    config_list: dict[str, DockerConfig],
    *,
    clean: bool = False,
) -> list[DockerContainerInfo]:
    """
    Generate, build, and run containers from the default config list.

    Args:
        config_list (dict[str, DockerConfig]): Docker image profiles to generate
            files from.
        clean (bool, optional): If True, remove generated files and images
            after execution.

    """
    typer.echo(f"Container Tests: {len(config_list)}")

    info_list = [
        test_container(
            cfg["os_name"],
            tag,
            cfg["command"],
            cfg["os_commands"],
            clean=clean,
        )
        for tag, cfg in config_list.items()
    ]

    return info_list
