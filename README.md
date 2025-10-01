# Container-tester

<h1 align="center">
	<img
        height="250"
		alt="narwhals_small"
		src="./logo.png">
</h1>

## Overview

Container-Tester is a small Python utility that helps you test your project on top of many different Linux distributions without having to write and maintain lots of Dockerfiles yourself. It provides a command-line interface (CLI) that can:

- Generate a Dockerfile for a given base image and optional shell commands, using a simple template.
- Build that Dockerfile into a Docker image and report its size and metadata.
- Run a container from that image, execute a command inside it and capture the logs.
- Optionally clean up Dockerfiles, images and containers when you are done.
- Iterate over a curated list of popular Python, Debian/Ubuntu, Fedora and Alpine base images defined in `docker-config.toml` and perform the above steps for each of them.

Container-Tester uses the Docker SDK for Python to communicate with your local Docker daemon. If Docker is not running, it prints a helpful error message and exits. The tool emits machine-readable JSON describing every step so you can integrate it into other scripts or CI pipelines.
