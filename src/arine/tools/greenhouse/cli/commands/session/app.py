from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

from typeguard import check_type
from typer import Context, Option, Typer

from arine.tools.greenhouse.browser.greenhouse.recruiting import GreenHouseRecruitingBrowser

session_app = Typer(name="session")


@session_app.callback()
def session_app_callback(
    ctx: Context,
    firefox_profile_path: Annotated[Path, Option()],
):
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj["firefox_profile_path"] = firefox_profile_path


@session_app.command(name="check")
def session_app_check(ctx: Context):
    ctx_obj = ctx.ensure_object(dict)
    firefox_profile_path = check_type(ctx_obj["firefox_profile_path"], Path)

    with TemporaryDirectory() as temp_dir:
        download_path = Path(temp_dir)
        with GreenHouseRecruitingBrowser(firefox_profile_path, download_path) as greenhouse_recruiting_browser:
            greenhouse_recruiting_browser.login()
