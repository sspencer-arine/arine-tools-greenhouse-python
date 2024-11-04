from pathlib import Path
from typing import Annotated

from typer import Context, Option, Typer

from arine.tools.greenhouse.cli.commands.recruiting.applications.app import recruiting_applications_app
from arine.tools.greenhouse.cli.commands.recruiting.jobs.app import recruiting_jobs_app

recruiting_app = Typer(name="recruiting")
recruiting_app.add_typer(recruiting_applications_app)
recruiting_app.add_typer(recruiting_jobs_app)


@recruiting_app.callback()
def recruiting_app_callback(
    ctx: Context,
    firefox_profile_path: Annotated[Path, Option()],
):
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj["firefox_profile_path"] = firefox_profile_path
