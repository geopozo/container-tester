"""Class to create, build and run docker containers."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any

import typer
from docker.errors import (
    APIError,
    ImageNotFound,
)

from container_tester import _utils

if TYPE_CHECKING:
    from docker import DockerClient


class DockerBackend:
    """Manages Dockerfile creation, image building, and container execution."""

    client: DockerClient

    def __init__(self, os_name: str) -> None:
        """Initialize the Docker backend client."""
        self.os_name = self._get_os_name(os_name)

    def _get_os_name(self, os_name: str) -> str:
        try:
            image = self.client.images.pull(os_name)
            verified_name = image.attrs.get("RepoTags", "")
        except (APIError, ImageNotFound) as e:
            typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
            sys.exit(1)
        else:
            return verified_name

    def _get_template(self, os_commands: list[str]) -> str:
        uv_copy = "COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"
        cmds = "\n".join(f"RUN {cmd}" for cmd in os_commands) if os_commands else ""

        return f"FROM {self.os_name}\n{uv_copy}\nWORKDIR /app\nADD . /app\n{cmds}"

    def generate(self, path: str, os_commands: list[str]) -> dict[str, Any]:
        """
        Generate a Dockerfile at the specified path.

        Args:
            path (str): Directory to save the Dockerfile.
            os_commands (list[str]): List of shell commands to include in the
                Dockerfile.

        Returns:
            dict: A dictionary with the keys:
                - 'name': Name of the generated Dockerfile.
                - 'full_path': Full path to the generated Dockerfile.
                - 'os_name': Name of the operating system used for the Dockerfile.

        Raises:
            SystemExit: If the Dockerfile generation fails due to an OSError,
                TypeError, or ValueError.

        """
        suffix_file_name = re.sub(r"[^a-zA-Z0-9]", "", self.os_name)

        try:
            dir_path = _utils.resolve_dir_path(path, mkdir=True)
            df_name = f"Dockerfile.{suffix_file_name}"
            content = self._get_template(os_commands)
            (dir_path / df_name).write_text(content)
        except (OSError, TypeError, ValueError) as e:
            typer.secho(
                f"Failed to generate Dockerfile: {e}",
                fg=typer.colors.RED,
                err=True,
            )
            sys.exit(1)
        else:
            return {
                "name": df_name,
                "full_path": (dir_path / df_name).as_posix(),
                "os_name": self.os_name,
            }

    def build(self):
        """Build docker image and optionally remove a tagged Docker image."""

    def run(self):
        """Run a container from a Docker image with the given command."""
