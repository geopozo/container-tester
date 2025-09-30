"""Docker config file list."""

from __future__ import annotations

from typing import TypedDict


class DockerConfig(TypedDict):
    """Type a docker config."""

    image_tag: str
    os_name: str
    commands: list[str]
    pkg_manager: str


cmd_certif = "apt-get update && apt-get install -y ca-certificates"

cfg_list: list[DockerConfig] = [
    {
        "image_tag": "py312_trixie",
        "os_name": "python:3.12-slim-trixie",
        "commands": [],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "py311_slim",
        "os_name": "python:3.11-slim",
        "commands": [],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "py310_slim",
        "os_name": "python:3.10-slim",
        "commands": [],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "debian_bookworm",
        "os_name": "debian:bookworm-slim",
        "commands": [cmd_certif],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "debian_bullseye",
        "os_name": "debian:bullseye-slim",
        "commands": [cmd_certif],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "ubuntu_latest",
        "os_name": "ubuntu:latest",
        "commands": [cmd_certif],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "ubuntu_20",
        "os_name": "ubuntu:20.04",
        "commands": [cmd_certif],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "ubuntu_22",
        "os_name": "ubuntu:22.04",
        "commands": [],
        "pkg_manager": "apt",
    },
    {
        "image_tag": "fedora_latest",
        "os_name": "fedora:latest",
        "commands": [],
        "pkg_manager": "dnf",
    },
    {
        "image_tag": "alpine_latest",
        "os_name": "alpine:latest",
        "commands": [],
        "pkg_manager": "apk",
    },
    {
        "image_tag": "alpine_3_18",
        "os_name": "alpine:3.19",
        "commands": [],
        "pkg_manager": "apk",
    },
    {
        "image_tag": "alpine_3_18",
        "os_name": "alpine:3.18",
        "commands": [],
        "pkg_manager": "apk",
    },
    {
        "image_tag": "alpine_3_17",
        "os_name": "alpine:3.17",
        "commands": [],
        "pkg_manager": "apk",
    },
]
