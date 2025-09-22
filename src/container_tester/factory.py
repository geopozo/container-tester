"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import pathlib
import sys
import time

import docker
from docker.errors import BuildError, ContainerError, DockerException, ImageNotFound

from container_tester import config

# ruff: noqa: T201 allow print in CLI


try:
    client = docker.from_env()
    client.ping()
except DockerException:
    print("Docker is not running. Please start the Docker daemon and try again.")
    sys.exit(1)


def _dockerfile_content(os_name: str, commands: list[str]) -> str:
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


def _generate_file(df_name: str, os_name: str, commands: list[str]) -> None:
    content = _dockerfile_content(os_name, commands)
    pathlib.Path(df_name).write_text(content)
    print(f"'{df_name}' generated.")


def _build(image_tag: str, df_name: str) -> None:
    start_time = time.time()
    try:
        client.images.build(
            path=".",
            dockerfile=df_name,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )
    except BuildError as e:
        print(e.build_log)
    secs = time.time() - start_time
    size = client.images.get(image_tag).attrs["Size"] / (1024 * 1024)
    print(f"[{image_tag}] \033[94m{size:.1f} MB\033[0m | \033[93m{secs:.1f}s\033[0m")


def _run(image_tag: str) -> None:
    try:
        output = client.containers.run(
            image_tag,
            command=["echo", "Hello"],
            name="choreo_base",
            tty=True,
            remove=True,
            stdout=True,
            stderr=True,
        )
        print(output.decode("utf-8", errors="replace"))
    except ContainerError as e:
        msg = (
            e.stderr.decode("utf-8", errors="replace")
            if isinstance(e.stderr, (bytes, bytearray))
            else str(e.stderr)
        )
        print(f"Container failed:\n{msg}")
    except ImageNotFound as e:
        print(f"Image not found: {e.explanation or e}")
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")


def _clean(
    os_name: str,
    image_tag: str,
    *,
    remove_base: bool = False,
) -> None:
    try:
        client.images.remove(image=image_tag, force=True)
    except (ImageNotFound, DockerException):
        pass
    if remove_base:
        try:
            client.images.remove(image=os_name, force=True)
        except (ImageNotFound, DockerException):
            pass
    try:
        client.images.prune(filters={"dangling": True})
    except DockerException:
        pass


def main() -> None:
    """Initialize the program."""
    for cfg in config.cfg_list:
        image_tag = cfg["name"]
        os_name = cfg["os_name"]
        commands = cfg["commands"]
        df_name = f"Dockerfile.{image_tag}"

        try:
            _generate_file(df_name, os_name, commands)
            _build(image_tag, df_name)
            _run(image_tag)
        except (ImageNotFound, BuildError, Exception) as e:
            print(f"ERROR: {e}")
            _clean(os_name, image_tag)
        finally:
            _clean(os_name, image_tag)
