# Container-tester

<h1 align="center">
	<img
        height="250"
		alt="container_small"
		src="./docs/media/logo.png">
</h1>

## Overview

Container-Tester is a small Python utility that helps you test your project on top of many different Linux distributions without having to run and maintain lots of Docker tests yourself. It provides a command-line interface (CLI) that can:

- Build that Dockerfile into a image and report its size and metadata.
- Run a container from that image, execute a command inside it and capture the logs.
- Optionally clean up images and containers when you are done.
- Iterate over a curated list of popular Python, Debian/Ubuntu, Fedora and Alpine base images defined in `docker-config.toml` and perform the above steps for each of them.

## Installation

You can use Container-Tester in two ways:

1. Install in your project:

<div class="termy">

```console
uv add container‑tester
```

</div>

After installation, verify that it’s working by running:

<div class="termy">

```console
uv run contest --help
```

</div>

2. From source using uvx (recommended for latest version):

<div class="termy">

```console
uvx --from container-tester contest --help
```

</div>

## Using Container-tester

<div class="termy">

```console
Usage: contest [OPTIONS] [OS_NAME]

Generate, build, and run Docker resources from a base image or config file.

╭─ Arguments ────────────────────────────────────────────────────────────────────╮
│ os_name      [OS_NAME]  [default: all]                                         |
╰────────────────────────────────────────────────────────────────────────────────╯

╭─ Options ──────────────────────────────────────────────────────────────────────╮
│ --name                 TEXT  Custom name for the generated Dockerfile.         │
│ --command              TEXT  Shell command to execute inside the containers.   │
│ --clean   --no-clean         Clean Docker resources after run                  │
│                              (use --clean to enable) [default: no-clean]       │
│ --json    --no-json          Show output in json format                        │
│                              (use --json to enable) [default: no-json]         │
│ --pretty  --no-pretty        Show output in pretty format                      │
│                              (use --pretty to enable) [default: no-pretty]     │
│ --help                       Show this message and exit.                       │
╰────────────────────────────────────────────────────────────────────────────────╯
```

</div>

### Example

Here is a quick example that runs a simple command across all default profiles:

<div class="termy">

```console
uv run contest --command "python --version"
```

</div>

To test only on the Ubuntu image, you can specify its base image directly and use a custom command:

<div class="termy">

```console
uv run contest ubuntu:latest --command "echo Hello, world!"
```

</div>

## Default profiles

By default, Container‑Tester comes with a handful of profiles covering common Python, Debian/Ubuntu and Alpine base images. Each profile defines an `image_tag` (used as the resulting image name) and the corresponding `os_name`. A few of them are shown below—see `src/container_tester/docker‑config.toml` for the full list:

| image_tag     | os_name                 |
| ------------- | ----------------------- |
| py312_trixie  | python:3.12‑slim‑trixie |
| ubuntu_latest | ubuntu:latest           |
| alpine_latest | alpine:latest           |

## Custom Docker Configuration

You can define your own `docker-config.toml` file to run custom Docker images tailored to your needs. Use the following format to specify multiple profiles:

```toml
[docker_config]

[[docker_config.profile]]
image_tag = "alpine_latest"
os_name = "alpine:latest"
os_commands = []
pkg_manager = "apk"

[[docker_config.profile]]
image_tag = "fedora_latest"
os_name = "fedora:latest"
os_commands = []
pkg_manager = "dnf"

# Add more profiles as needed...
```

### Configuration Fields

- `image_tag`: A unique identifier for the Docker image profile.
- `os_name`: The name and tag of the Docker image to use.
- `os_commands`: A list of shell commands to run after container startup (optional).
- `pkg_manager`: The package manager used by the OS (e.g., apk, dnf, apt).

### Run with Your Custom Config

After creating your `docker-config.toml` file, launch your custom Docker setup by running:

<div class="termy">

```console
uv run contest
```

</div>

## License

This project is licensed under the terms of the MIT license.
