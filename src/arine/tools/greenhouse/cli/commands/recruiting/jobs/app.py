from pathlib import Path
from tempfile import TemporaryDirectory

from diskcache import Cache
from typeguard import check_type
from typer import Context, Typer, echo

from arine.tools.greenhouse.browser.greenhouse.recruiting import GreenHouseRecruitingBrowser
from arine.tools.greenhouse.models.greenhouse.recruiting.jobs import GreenhouseRecruitingJob

recruiting_jobs_app = Typer(name="jobs")


@recruiting_jobs_app.callback()
def recruiting_jobs_app_callback():
    pass


@recruiting_jobs_app.command(name="list")
def recruiting_jobs_app_command_list(ctx: Context):
    ctx_obj = ctx.ensure_object(dict)
    firefox_profile_path = check_type(ctx_obj["firefox_profile_path"], Path)

    with TemporaryDirectory() as temp_dir, Cache(".cache") as cache:
        download_path = Path(temp_dir)
        with GreenHouseRecruitingBrowser(firefox_profile_path, download_path) as greenhouse_recruiting_browser:
            greenhouse_recruiting_jobs = check_type(
                cache.get("greenhouse_recruiting_jobs", []), list[GreenhouseRecruitingJob]
            )
            if not greenhouse_recruiting_jobs:
                greenhouse_recruiting_jobs = list(greenhouse_recruiting_browser.all_jobs())
                cache.set("greenhouse_recruiting_jobs", greenhouse_recruiting_jobs)

            for greenhouse_recruiting_job in greenhouse_recruiting_jobs:
                echo(greenhouse_recruiting_job)
