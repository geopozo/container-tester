import re
from typing import Annotated

import rich
import typer

from container_tester import _utils, app


def _print_output(data: app.DockerInfo | None) -> None:
    if not data:
        typer.echo("No data.")
        return

    stdout = data.get("container").get("stdout", "")
    stderr = data.get("container").get("stderr", "")

    typer.echo(stdout) if stdout else None
    typer.echo(stderr, err=True) if stderr else None


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
    path: Annotated[
        str,
        typer.Option(
            help="Directory to create or retrieve Dockerfiles. (default: all).",
        ),
    ] = "",
    command: Annotated[
        str,
        typer.Option(help="Shell command to execute inside the containers."),
    ] = "",
    *,
    clean: Annotated[
        bool,
        typer.Option(help="Clean Docker resources after run (use --clean to enable)"),
    ] = False,
    json: Annotated[
        bool,
        typer.Option(help="Show output in json format (use --json to enable)"),
    ] = False,
    pretty: Annotated[
        bool,
        typer.Option(help="Show output in pretty format (use --pretty to enable)"),
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

    if not path:
        path = str(_utils.get_cwd())

    if os_name == "all":
        cfg_list = _utils.load_config()
        out = app.run_config(path, cfg_list, command, clean=clean)
    else:
        out = app.test_container(os_name, name, path, command, clean=clean)

    if json:
        out = _utils.format_json(out)
        rich.print_json(out, highlight=pretty)
    elif isinstance(out, list):
        for v in out:
            _print_output(v)
    else:
        _print_output(out)


def run_cli() -> None:
    typer.run(main)
