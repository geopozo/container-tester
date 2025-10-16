import re
from typing import Annotated

import rich
import typer

from container_tester import _utils, app


def _print_output(data: app.DockerInfo) -> None:
    test_name = data.get("image", {}).get("name", "")
    stdout = data.get("container", {}).get("stdout", "")
    stderr = data.get("container", {}).get("stderr", "")

    typer.echo(f"\nTest {test_name}:\n{stdout}")

    if stderr:
        typer.echo(stderr, err=True)


def main(  # noqa: PLR0913
    os_name: Annotated[
        str,
        typer.Argument(
            help="Base Docker image to initialize from (e.g., 'ubuntu:20.04').",
        ),
    ] = "all",
    name: Annotated[
        str,
        typer.Option(help="Custom name for the generated Dockerfile"),
    ] = "",
    command: Annotated[
        str,
        typer.Option(help="Shell command to execute inside the containers."),
    ] = "",
    *,
    clean: Annotated[
        bool,
        typer.Option(help="Clean Docker resources after run."),
    ] = False,
    json: Annotated[
        bool,
        typer.Option(help="Show output in json format."),
    ] = False,
    pretty: Annotated[
        bool,
        typer.Option(help="Show output in pretty format."),
    ] = False,
) -> None:
    """Generate, build, and run Docker resources from a base image or config file."""
    os_name = os_name.lower().strip()

    if not os_name:
        raise ValueError("The 'os-name' option cannot be empty.")

    if name and os_name == "all":
        raise typer.BadParameter(
            f"Cannot use --name '{name}' without specifying os-name.",
            param_hint="--name",
        )

    if name and not re.fullmatch(r"[a-zA-Z0-9]+", name):
        raise typer.BadParameter(
            f"Invalid name '{name}'. Must contain only letters and digits",
            param_hint="--name",
        )

    if os_name == "all":
        cfg_list = _utils.load_config()
        data = app.run_config(cfg_list, command, clean=clean)
    else:
        data = app.test_container(os_name, name, command, clean=clean)

    if not data:
        typer.echo("No data.")
        return

    if json:
        data = _utils.format_json(data)
        rich.print_json(data, highlight=pretty)
    elif isinstance(data, list):
        for v in data:
            _print_output(v)
    else:
        _print_output(data)


def run_cli() -> None:
    typer.run(main)
