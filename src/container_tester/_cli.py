import re

import click

from container_tester import _utils, app

# ruff: noqa: T201 allow print in CLI


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
@click.option(
    "--pretty",
    default=False,
    is_flag=True,
    help="Show output in Pretty format",
)
def run_cli(  # noqa: PLR0913
    os_name: str,
    name: str,
    path: str,
    command: str,
    *,
    clean: bool = False,
    pretty: bool = False,
) -> None:
    """
    Generate, build, and run Docker resources from a base image or config list.

    OS_NAME base Docker image to initialize from (e.g., 'ubuntu:20.04').
        (default: all).

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
        out = app.run_config(path, clean=clean)
    else:
        out = app.test_container(os_name, name, path, command, clean=clean)

    click.echo(_utils.format_json(out, pretty=pretty))
