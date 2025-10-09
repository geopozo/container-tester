"""Class to create, build and run docker containers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docker import DockerClient


class DockerBackend:
    """Manages Dockerfile creation, image building, and container execution."""

    client: DockerClient

    def __init__(self):
        """Initialize the Docker backend client."""

    def generate(self):
        """Generate a Dockerfile for the given OS and name at the specified path."""

    def build(self):
        """Build docker image and optionally remove a tagged Docker image."""

    def run(self):
        """Run a container from a Docker image with the given command."""
