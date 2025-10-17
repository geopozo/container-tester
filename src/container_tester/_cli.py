import re
from typing import Annotated, Any

import rich
import typer

from container_tester import _utils, app

cli = typer.Typer()
flags = {"json": False, "pretty": False, "clean": False}


def _print_output(data: dict[str, Any]) -> None:
    if flags["json"]:
        data_json = _utils.format_json(data)
        rich.print_json(data_json, highlight=flags["pretty"])
        return

    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")

    if stdout:
        typer.echo(stdout)

    if stderr:
        typer.echo(stderr, err=True)


@cli.command()
def test_config():
    """Generate, build, and run Docker resources from a docker config."""
    cfg_list = _utils.load_config()
    data = app.run_config(cfg_list, clean=flags["clean"])

    for value in data:
        _print_output(value)


@cli.command()
def test_container(
    os_name: Annotated[
        str,
        typer.Argument(
            help="Base Docker image to initialize from (e.g., 'ubuntu:20.04').",
        ),
    ] = "",
    name: Annotated[
        str,
        typer.Option(help="Custom name for the generated docker image"),
    ] = "",
    command: Annotated[
        str,
        typer.Option(help="Shell command to execute inside the containers."),
    ] = "",
):
    """Generate, build, and run Docker resources from a base image."""
    os_name = os_name.lower().strip()

    if not os_name:
        raise ValueError("The 'os-name' option cannot be empty.")

    if name and not re.fullmatch(r"[a-zA-Z0-9]+", name):
        raise typer.BadParameter(
            f"Invalid name '{name}'. Must contain only letters and digits",
            param_hint="--name",
        )

    data = app.test_container(os_name, name, command, clean=flags["clean"])

    _print_output(data)


@cli.callback()
def main(
    *,
    json: Annotated[
        bool,
        typer.Option(help="Show output in json format."),
    ] = False,
    pretty: Annotated[
        bool,
        typer.Option(help="Show output in pretty format."),
    ] = False,
    clean: Annotated[
        bool,
        typer.Option(help="Clean Docker resources after run."),
    ] = False,
) -> None:
    flags["json"] = json
    flags["pretty"] = pretty
    flags["clean"] = clean
