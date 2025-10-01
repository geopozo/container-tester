import re
from typing import Annotated

import rich
import typer

from container_tester import _utils, app

# ruff: noqa: T201 allow print in CLI


def main(  # noqa: PLR0913
    os_name: Annotated[str, typer.Argument()] = "all",
    name: Annotated[
        str,
        typer.Option(help="Custom name for the generated Dockerfile or Image"),
    ] = "",
    path: Annotated[
        str,
        typer.Option(help="Directory to create or retrieve Dockerfiles."),
    ] = "",
    command: Annotated[
        str,
        typer.Option(help="Shell command to execute inside the container."),
    ] = "",
    *,
    clean: Annotated[
        bool,
        typer.Option(help="Clean Docker resources after run (use --clean to enable)"),
    ] = False,
    pretty: Annotated[
        bool,
        typer.Option(help="Show output in Pretty format (use --pretty to enable)"),
    ] = False,
) -> None:
    """Generate, build, and run Docker resources from a base image or config list."""
    os_name = os_name.lower().strip()

    if not os_name:
        raise ValueError("The 'os-name' option cannot be empty.")

    if not name:
        name = re.sub(r"[^a-zA-Z0-9]", "", os_name)

    if not re.fullmatch(r"[a-zA-Z0-9]+", name):
        raise typer.BadParameter(
            f"Invalid name '{name}'. Must contain only letters and digits",
            param_hint="--name",
        )

    if not path:
        path = str(_utils.get_cwd())

    if os_name == "all":
        cfg_list = _utils.load_config()
        out = app.run_config(path, cfg_list, command, clean=clean)
    else:
        out = app.test_container(os_name, name, path, command, clean=clean)

    rich.print(out) if pretty else typer.echo(out)


def run_cli():
    typer.run(main)
