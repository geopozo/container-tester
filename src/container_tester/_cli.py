import re

import click

from container_tester import factory


@click.group(help=("CLI for testing containers."))
@click.option(
    "--all",
    is_flag=True,
    help="Run all images in config file.",
    callback=factory.default_config(path="."),
    expose_value=False,
    is_eager=True,
)
def cli() -> None:
    """CLI for test containers."""


@cli.command()
@click.argument("name")
@click.option(
    "--path",
    default=".",
    help="Directory containing the Dockerfile (default: current)",
)
@click.option(
    "--clean/--no-clean",
    default=False,
    is_flag=True,
    help="Delete Docker image after build (use --clean to enable)",
)
def build(name: str, path: str, *, clean: bool = False) -> None:
    """
    Build a Docker image from a tagged Dockerfile.

    NAME for the Docker image. Required.
    """
    if not name.strip():
        raise click.BadParameter("The '--name' option cannot be empty.")

    factory.build_image(name, path, clean=clean)


@cli.command()
@click.argument("os-name")
@click.option("--name", default="", help="Name for the generated Dockerfile")
@click.option(
    "--path",
    default=".",
    help="Directory to create or retrieve Dockerfiles. (default: current)",
)
def generate_file(os_name: str, name: str, path: str) -> None:
    """
    Generate a Dockerfile based on a given base image.

    OS_NAME base Docker image to initialize from (e.g., 'ubuntu:20.04')
    """
    if not os_name.strip():
        raise click.BadParameter("The '--os-name' option cannot be empty.")

    if not name:
        name = re.sub(r"[^a-zA-Z0-9]", "", os_name)

    factory.generate_file(os_name, name, path)


@cli.command()
@click.argument("name")
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
    help="Delete Docker container after run (use --clean to enable)",
)
def run(name: str, command: str, *, clean: bool = False) -> None:
    """
    Run a Docker container from a tagged docker image.

    NAME for the Docker image. Required.
    """
    if not name.strip():
        raise click.BadParameter("The '--name' option cannot be empty.")

    if not command.strip():
        raise click.BadParameter("The '--command' option cannot be empty.")

    factory.run_container(name, command, clean=clean)


@cli.command()
@click.argument(
    "option",
    type=click.Choice(["container", "dockerfile", "image"], case_sensitive=False),
)
@click.option("--name", help="Name of the resource to remove (image or Dockerfile)")
@click.option(
    "--path",
    default=".",
    help="Directory to create or retrieve Dockerfiles (defaults to current directory)",
)
def remove(option: str, name: str, path: str) -> None:
    """Remove a Docker resource: container, image, or Dockerfile."""
    if not name:
        raise click.UsageError("You must provide --name to remove an resource.")

    if option == "container":
        factory.remove_container(name)
    elif option == "dockerfile":
        factory.remove_dockerfile(name, path)
    elif option == "image":
        factory.remove_image(name)
