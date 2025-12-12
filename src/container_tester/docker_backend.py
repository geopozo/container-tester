"""Class to create, build and run docker containers."""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import docker
import rich
import typer
from docker.errors import (
    APIError,
    BuildError,
    ContainerError,
    DockerException,
    ImageNotFound,
    NotFound,
)
from platformdirs import user_cache_dir

from container_tester import _utils

if TYPE_CHECKING:
    from docker import DockerClient
    from docker.models.containers import Container as DockerContainer


@dataclass
class DockerImageInfo:
    """Docker image build data."""

    name: str
    os_name: str
    os_base: str
    os_architecture: str
    size: str

    def print(self, *, json: bool = False, pretty: bool = False) -> None:
        """
        Print image output.

        Args:
            json (bool): Whether to output the data in JSON format.
            pretty (bool): Whether to pretty-print the output.

        """
        data = {
            "name": self.name,
            "os_name": self.os_name,
            "os_base": self.os_base,
            "os_architecture": self.os_architecture,
            "size": self.size,
        }
        if json:
            data_json = _utils.format_json(data)
            rich.print_json(data_json, highlight=pretty)
        elif pretty:
            rich.print(_utils.format_table("image", data, pretty=pretty))
        else:
            typer.echo(data)


@dataclass
class DockerContainerInfo:
    """Docker container data."""

    id: str | None
    name: str
    command: str
    stdout: str
    stderr: str

    def print(self, *, json: bool = False, pretty: bool = False) -> None:
        """
        Print container output.

        Args:
            json (bool): Whether to output the data in JSON format.
            pretty (bool): Whether to pretty-print the output.

        """
        data = {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }
        if json:
            data_json = _utils.format_json(data)
            rich.print_json(data_json, highlight=pretty)
        elif pretty:
            rich.print(_utils.format_table("container", data, pretty=pretty))
        else:
            if self.stdout:
                typer.echo(self.stdout)

            if self.stderr:
                typer.echo(self.stderr, err=True)


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

    def __init__(
        self,
        os_name: str,
        *,
        image_tag: str = "",
        command: str = "",
        os_commands: list[str] | None = None,
    ) -> None:
        """Initialize the Docker backend client."""
        self.client = self._docker_client()
        self.os_name = self._get_os_name(os_name)
        self.image_tag = image_tag or self._get_tag_name(self.os_name)
        self.command = command or 'echo "Container is running"'
        self.os_commands = os_commands or []

    def _get_os_name(self, os_name: str) -> str:
        try:
            image = self.client.images.pull(os_name)
            verified_name = image.attrs.get("RepoTags", "")[0]
        except (APIError, ImageNotFound) as e:
            typer.secho(
                f"Failed to retrieve image '{os_name}'.\n{e}",
                fg=typer.colors.RED,
                err=True,
            )
            sys.exit(1)
        else:
            return verified_name

    def _get_template(self) -> str:
        uv_copy = "COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"
        cmds = (
            "\n".join(f"RUN {cmd}" for cmd in self.os_commands)
            if self.os_commands
            else ""
        )

        return f"FROM {self.os_name}\n{uv_copy}\nWORKDIR /app\nCOPY . /app\n{cmds}"

    def _generate_file(self, content: str) -> Path:
        temp_dir = Path(user_cache_dir("container_tester"))
        temp_dir.mkdir(parents=True, exist_ok=True)

        file = temp_dir / "Dockerfile"
        file.write_text(content, encoding="utf-8")

        return file

    def build(self) -> DockerImageInfo:
        """
        Build docker image and optionally remove a tagged Docker image.

        Raises:
            SystemExit: If the Docker build fails due to an BuildError,
                APIError, or TypeError.

        """
        content = self._get_template()
        dockerfile = self._generate_file(content)

        try:
            image, _ = self.client.images.build(
                path=str(_utils.get_cwd()),
                dockerfile=str(dockerfile),
                tag=self.image_tag,
                rm=True,  # Necessary to remove intermediate containers.
                forcerm=True,  # Necessary to remove intermediate containers.
            )
            size = image.attrs.get("Size", "") / (1024 * 1024)

            return DockerImageInfo(
                name=self.image_tag,
                os_name=self.os_name,
                os_base=image.attrs["Os"],
                os_architecture=image.attrs["Architecture"],
                size=f"{size:.2f} MB",
            )
        except (BuildError, APIError, TypeError) as e:
            error_msg = getattr(e, "msg", str(e))
            typer.secho(
                f"Failed to build Docker image '{self.image_tag}'.\n{error_msg}",
                fg=typer.colors.RED,
                err=True,
            )
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
        except (NotFound, APIError) as e:
            typer.secho(
                f"Failed to remove container '{container_id}'.\n{e}",
                fg=typer.colors.RED,
                err=True,
            )

    def run(self) -> DockerContainerInfo:
        """
        Run a container from a Docker image with the given command.

        Raises:
            SystemExit: If the Docker build fails due to an ContainerError,
                ImageNotFound, or APIError.

        """
        timestamp = int(time.time())
        container_name = f"container_test_{self.image_tag}_{timestamp}"

        try:
            container = self.client.containers.run(
                self.image_tag,
                command=self.command,
                name=container_name,
                detach=True,
                stdout=True,
                stderr=True,
            )
            result = container.wait()

            exit_code = result.get("StatusCode")
            stdout_logs = container.logs(stdout=True, stderr=False).decode()
            stderr_logs = container.logs(stdout=False, stderr=True).decode()
            config = container.attrs.get("Config", {})

            return DockerContainerInfo(
                id=container.id,
                name=container_name,
                command=config.get("Cmd"),
                stdout=stdout_logs.strip(),
                stderr=stderr_logs.strip() if exit_code else "",
            )

        except (ContainerError, ImageNotFound, APIError) as e:
            typer.secho(
                f"Failed to run container from image '{self.image_tag}'.\n{e}",
                fg=typer.colors.RED,
                err=True,
            )
            sys.exit(1)

    def remove_image(self) -> None:
        """
        Remove a Docker image by image-tag.

        Raises:
            DockerException: If the image removal fails due to an API error or
                other Docker-related exception.

        """
        try:
            self.client.images.remove(image=self.image_tag, force=True)
        except (APIError, DockerException, ImageNotFound) as e:
            raise DockerException(f"Failed to remove Docker image.\n{e}") from e

    def remove_dangling(self) -> None:
        """Remove dangling Docker images to free up space."""
        try:
            self.client.images.prune(filters={"dangling": True})
        except DockerException:
            typer.secho(
                "Failed to remove dangling.",
                fg=typer.colors.YELLOW,
                err=True,
            )
