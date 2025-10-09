"""Class to create, build and run docker containers."""

from __future__ import annotations

import re
import sys
import time
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from docker import DockerClient
    from docker.models.containers import Container as DockerContainer


class DockerBackend:
    """Manages Dockerfile creation, image building, and container execution."""

    client: DockerClient

    def _get_tag_name(self, name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "_", name)

    def _docker_client(self) -> DockerClient:
        """Return a ready Docker client."""
        try:
            return docker.from_env()
        except DockerException:
            typer.echo(
                "Docker is not running. Please start the Docker daemon and try again.",
                err=True,
            )
            sys.exit(1)

    def __init__(self, os_name: str) -> None:
        """Initialize the Docker backend client."""
        self.client = self._docker_client()
        self.os_name = self._get_os_name(os_name)

    def _get_os_name(self, os_name: str) -> str:
        try:
            image = self.client.images.pull(os_name)
            verified_name = image.attrs.get("RepoTags", "")[0]
        except (APIError, ImageNotFound) as e:
            typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
            sys.exit(1)
        else:
            return verified_name

    def _get_template(self, os_commands: list[str] | None) -> str:
        uv_copy = "COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"
        cmds = "\n".join(f"RUN {cmd}" for cmd in os_commands) if os_commands else ""

        return f"FROM {self.os_name}\n{uv_copy}\nWORKDIR /app\nADD . /app\n{cmds}"

    def generate(
        self,
        path: str,
        *,
        image_tag: str = "",
        os_commands: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a Dockerfile at the specified path.

        Args:
            path (str): Directory to save the Dockerfile.
            image_tag (str): Identifier used in the Dockerfile name.
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
        suffix_file_name = image_tag or self._get_tag_name(self.os_name)

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

    def build(self, path: str, image_tag: str = "") -> dict[str, Any]:
        """
        Build docker image and optionally remove a tagged Docker image.

        Args:
            path (str): Directory containing the Dockerfile.
            image_tag (str): Tag for the resulting Docker image.

        Returns:
            dict: A dictionary with the following keys:
                - 'name': Name of the image tag.
                - 'os': Dictionary with OS metadata including:
                    - 'architecture': CPU architecture of the image.
                    - 'base': Base operating system of the image.
                - 'size': Size of the image in megabytes, formatted as a string.

        Raises:
            SystemExit: If the Docker build fails due to an BuildError,
                APIError, or TypeError.

        """
        image_tag = image_tag or self._get_tag_name(self.os_name)

        try:
            df_name = f"Dockerfile.{image_tag}"
            dir_path = _utils.resolve_dir_path(path)
            image, _ = self.client.images.build(
                path=f"{dir_path!s}",
                dockerfile=df_name,
                tag=image_tag,
                rm=True,
                forcerm=True,
            )
            size = image.attrs.get("Size", "") / (1024 * 1024)

            return {
                "name": image_tag,
                "os": {
                    "architecture": image.attrs["Architecture"],
                    "base": image.attrs["Os"],
                },
                "size": f"{size:.2f} MB",
            }
        except BuildError as e:
            typer.secho(e.msg, fg=typer.colors.RED, err=True)
            sys.exit(1)
        except (APIError, TypeError) as e:
            typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
            sys.exit(1)

    def remove_container(self, container_id: str) -> None:
        """
        Remove a Docker container by container_id.

        Args:
            container_id (str): Container name or ID to remove.

        """
        try:
            containers: list[DockerContainer] = self.client.containers.list(all=True)

            for container in containers:
                if container_id in (container.name, container.id):
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

    def run(
        self,
        image_tag: str = "",
        command: str = "",
        *,
        clean: bool = False,
    ) -> dict[str, Any]:
        """
        Run a container from a Docker image with the given command.

        Args:
            image_tag (str): Tag of the image to run.
            command (str): Command to execute inside the container.
            clean (bool, optional): If True, remove the container after execution.
                Defaults to False.

        Returns:
            dict: A dictionary with the following keys:
                - 'id': ID of the generated container.
                - 'name': Name assigned to the container.
                - 'command': Command executed inside the container.
                - 'stdout': Standard output from the container execution.
                - 'stderr': Standard error from the container execution.

        Raises:
            SystemExit: If the Docker build fails due to an ContainerError,
                ImageNotFound, or APIError.

        """
        image_tag = image_tag or self._get_tag_name(self.os_name)
        command = command or 'echo "Container is running"'
        timestamp = int(time.time())
        container_name = f"container_test_{image_tag}_{timestamp}"

        try:
            container = self.client.containers.run(
                image_tag,
                command=command,
                name=container_name,
                detach=True,
                stdout=True,
                stderr=True,
            )
            container.wait()

            stdout_logs = container.logs(stdout=True, stderr=False).decode()
            stderr_logs = container.logs(stdout=False, stderr=True).decode()
            config = container.attrs.get("Config", {})

            if clean:
                self.remove_container(container_name)

            return {
                "id": container.id,
                "name": container_name,
                "command": config.get("Cmd"),
                "stdout": stdout_logs.strip(),
                "stderr": stderr_logs.strip(),
            }

        except (ContainerError, ImageNotFound, APIError) as e:
            typer.secho(f"{type(e).__name__}:\n{e}", fg=typer.colors.RED, err=True)
            sys.exit(1)

    def remove_dockerfile(
        self,
        path: str,
        image_tag: str = "",
    ) -> None:
        """
        Remove a Dockerfile matching the image tag from the given path.

        Args:
            path (str): Directory to search for the Dockerfile.
            image_tag (str): Tag used to identify the Dockerfile.

        """
        image_tag = image_tag or self._get_tag_name(self.os_name)
        df_name = f"Dockerfile.{image_tag}"

        try:
            dir_path = _utils.resolve_dir_path(path)
            (dir_path / df_name).unlink()
        except DockerException as e:
            typer.secho(
                f"Failed to remove '{df_name}': {e}",
                fg=typer.colors.RED,
                err=True,
            )
        except (TypeError, FileNotFoundError) as e:
            typer.secho(
                f"{type(e).__name__}:\n{e}",
                fg=typer.colors.RED,
                err=True,
            )

    def remove_image(self, image_tag: str = "") -> None:
        """
        Remove a Docker image by image-tag.

        Args:
            image_tag (str): Tag used to identify the docker image to remove.

        Raises:
            DockerException: If the image removal fails due to an API error or
                other Docker-related exception.

        """
        try:
            self.client.images.remove(image=image_tag, force=True)
        except ImageNotFound:
            typer.secho(f"Image '{image_tag}' not found.", fg=typer.colors.RED)
        except (APIError, DockerException) as e:
            raise DockerException("Failed to remove Docker image.") from e

    def remove_dangling(self) -> None:
        """Remove dangling Docker images to free up space."""
        try:
            self.client.images.prune(filters={"dangling": True})
        except DockerException:
            typer.secho("Failed to remove dangling.", fg=typer.colors.YELLOW)
