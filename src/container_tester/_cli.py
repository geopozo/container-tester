import re

import click

from container_tester import factory


@click.command()
@click.argument("os-name", default="all", required=False)
@click.option(
    "--name",
    default="",
    help="Custom name for the generated Dockerfile or Image",
)
@click.option(
    "--path",
    default=".",
    help="Directory to create or retrieve Dockerfiles. (default: current)",
)
@click.option(
    "--command",
    default="",
    type=str,
    help="Shell command to execute inside the container.",
)
@click.option(
    "--clean/--no-clean",
    default=False,
    is_flag=True,
    help="Clean Docker resources after run (use --clean to enable)",
)
def run_cli(
    os_name: str,
    name: str,
    path: str,
    *,
    command: str = "",
    clean: bool = False,
) -> None:
    """
    Generate, build, and run Docker containers from a base image or config list.

    OS_NAME base Docker image to initialize from (e.g., 'ubuntu:20.04').

    """
    if not os_name.strip():
        raise click.UsageError("The 'os-name' option cannot be empty.")

    if not name:
        name = re.sub(r"[^a-zA-Z0-9]", "", os_name)

    if not re.fullmatch(r"[a-zA-Z0-9]+", name):
        raise click.BadParameter(
            f"Invalid name '{name}'. Must contain only letters and digits",
            param_hint="--name",
        )

    if os_name.lower() == "all":
        factory.run_config(path, clean=clean)
    else:
        factory.test_container(os_name, name, path, command=command, clean=clean)
