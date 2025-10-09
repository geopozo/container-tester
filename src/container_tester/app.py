"""Run docker with test commands."""

from __future__ import annotations

from typing import Any, TypedDict

from container_tester.docker_backend import DockerBackend


class DockerConfig(TypedDict):
    """Type a docker config."""

    image_tag: str
    os_name: str
    os_commands: list[str]
    pkg_manager: str


class DockerInfo(TypedDict):
    """Type a docker info."""

    dockerfile: dict[str, Any]
    image: dict[str, Any]
    container: dict[str, Any]


def test_container(
    os_name: str,
    name: str,
    path: str,
    command: str,
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
        clean (bool): If True, remove generated artifacts after execution.

    """
    docker_test = DockerBackend(os_name)

    docker_info = DockerInfo(
        dockerfile=docker_test.generate(path, image_tag=name, os_commands=[]),
        image=docker_test.build(path, name),
        container=docker_test.run(name, command, clean=clean),
    )

    if clean:
        docker_test.remove_dockerfile(path, name)
        docker_test.remove_image(name)
        docker_test.remove_dangling()

    return docker_info
