"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import logging
import pathlib
import sys
import time

import docker
from docker.errors import BuildError, ContainerError, DockerException, ImageNotFound

from container_tester import _utils, config

# ruff: noqa: T201 allow print in CLI

logger = logging.getLogger(__name__)

try:
    client = docker.from_env()
    client.ping()
except DockerException:
    logger.warning(
        "Docker is not running. Please start the Docker daemon and try again.",
    )
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


def _generate_file(config: config.DockerConfig, dir_path: pathlib.Path) -> None:
    df_name = f"Dockerfile.{config['name']}"
    content = _dockerfile_content(config["os_name"], config["commands"])

    (dir_path / df_name).write_text(content)
    logger.info(f"'{df_name}' generated.")


def _build(config: config.DockerConfig, dir_path: pathlib.Path) -> None:
    image_tag = config["name"]
    df_name = f"Dockerfile.{image_tag}"
    start_time = time.time()

    try:
        client.images.build(
            path=str(dir_path),
            dockerfile=df_name,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )
    except BuildError as e:
        print(e.build_log)
    secs = time.time() - start_time
    size = client.images.get(image_tag).attrs["Size"] / (1024 * 1024)
    logger.info(
        f"[{image_tag}] \033[94m{size:.1f} MB\033[0m | \033[93m{secs:.1f}s\033[0m",
    )


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
        print(f"Container failed:\n{e.stderr}")
    except ImageNotFound as e:
        print(f"Image not found: {e.explanation or e}")
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")


def _clean_dangling() -> None:
    try:
        client.images.prune(filters={"dangling": True})
    except DockerException:
        pass


def _remove_image(image_tag: str):
    try:
        client.images.remove(image=image_tag, force=True)
    except (ImageNotFound, DockerException):
        pass


def main() -> None:
    """Initialize the program."""
    dir_path = _utils.resolve_dir_path("")
    remove_base = False

    for cfg in config.cfg_list:
        image_tag = cfg["name"]
        os_name = cfg["os_name"]

        try:
            _generate_file(cfg, dir_path)
            _build(cfg, dir_path)
            _run(image_tag)
        except (ImageNotFound, BuildError, Exception) as e:
            print(f"ERROR: {e}")
        finally:
            _clean_dangling()
            _remove_image(image_tag)
            if remove_base:
                _remove_image(os_name)
