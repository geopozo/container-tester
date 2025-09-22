"""Create, build and run docker containers with test commands."""

from __future__ import annotations

import pathlib
import sys
import time

import config
import docker
from docker.errors import BuildError, ContainerError, DockerException, ImageNotFound

# ruff: noqa: T201 allow print in CLI


try:
    client = docker.from_env()
    client.ping()
except DockerException:
    print("Docker is not running. Please start the Docker daemon and try again.")
    sys.exit(1)


def _generate_file(df_name: str, os_name: str, commands: list[str]) -> None:
    has_py = pathlib.Path("pyproject.toml").exists()
    has_lock = pathlib.Path("uv.lock").exists()
    deps = []
    if has_py:
        deps.append("COPY pyproject.toml /app/pyproject.toml")
    if has_lock:
        deps.append("COPY uv.lock /app/uv.lock")
    content = f"""FROM {os_name}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
{"\n".join(deps) if deps else ""}
ENV UV_LINK_MODE=copy
ADD . /app
RUN uv sync --locked
{"\n".join(f"RUN {cmd}" for cmd in commands) if commands else ""}
"""
    pathlib.Path(df_name).write_text(content)
    print(f"'{df_name}' has been successfully generated.")


def _build(image_tag: str, df_name: str):
    start_time = time.time()
    client.images.build(
        path=".",
        dockerfile=df_name,
        tag=image_tag,
        rm=True,
        forcerm=True,
    )
    secs = time.time() - start_time
    size = client.images.get(image_tag).attrs["Size"] / (1024 * 1024)
    print(f"[{image_tag}] \033[94m{size:.1f} MB\033[0m | \033[93m{secs:.1f}s\033[0m")


def _run(image_tag: str):
    try:
        output = client.containers.run(
            image_tag,
            command=["uv", "run", "_docker/script.py"],
            name="choreo_base",
            tty=True,
            remove=True,
            stdout=True,
            stderr=True,
        )
        print(output.decode("utf-8", errors="replace"))
    except ContainerError as e:
        print(f"Container failed: {e.stderr}")
    except ImageNotFound as e:
        print(f"Image not found: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")


def _clean(
    os_name: str,
    image_tag: str,
    df_name: str,
    *,
    remove_base: bool = False,
):
    client.images.remove(image=image_tag, force=True)
    if remove_base:
        client.images.remove(image=os_name, force=True)
    client.images.prune(filters={"dangling": True})
    pathlib.Path(df_name).unlink(missing_ok=True)


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
        _clean(os_name, image_tag, df_name, remove_base=True)
    finally:
        _clean(os_name, image_tag, df_name, remove_base=True)
