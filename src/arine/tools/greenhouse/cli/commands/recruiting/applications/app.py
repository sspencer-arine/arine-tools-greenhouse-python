from pathlib import Path, PosixPath
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Annotated
from urllib.parse import parse_qs, urlparse

from diskcache import Cache
from typeguard import check_type
from typer import Context, Option, Typer, echo

from arine.tools.greenhouse.browser.greenhouse.recruiting import GreenHouseRecruitingBrowser
from arine.tools.greenhouse.models.greenhouse.recruiting.jobs import (
    GreenhouseRecruitingJob,
    GreenhouseRecruitingJobApplication,
)

recruiting_applications_app = Typer(name="applications")


@recruiting_applications_app.callback()
def recruiting_candidates_app_callback(
    ctx: Context,
    job_title: Annotated[str, Option()],
):
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj["job_title"] = job_title


@recruiting_applications_app.command(name="list")
def recruiting_candidates_app_command_list(ctx: Context):
    ctx_obj = ctx.ensure_object(dict)
    firefox_profile_path = check_type(ctx_obj["firefox_profile_path"], Path)
    job_title = check_type(ctx_obj["job_title"], str)

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
                if greenhouse_recruiting_job.title == job_title:
                    break
            else:
                raise RuntimeError("Could not find job by title")

            greenhouse_recruiting_job_applications = check_type(
                cache.get(
                    f"greenhouse_recruiting_job_applications:{greenhouse_recruiting_job.title}",
                    [],
                ),
                list[GreenhouseRecruitingJobApplication],
            )

            if not greenhouse_recruiting_job_applications:
                greenhouse_recruiting_job_applications = list(
                    greenhouse_recruiting_browser.all_job_applications(greenhouse_recruiting_job)
                )
                cache.set(
                    f"greenhouse_recruiting_job_applications:{greenhouse_recruiting_job.title}",
                    greenhouse_recruiting_job_applications,
                )

            for greenhouse_recruiting_job_application in greenhouse_recruiting_job_applications:
                echo(greenhouse_recruiting_job_application)


@recruiting_applications_app.command(name="offline")
def recruiting_candidates_app_command_offline(ctx: Context, offline_path: Path):
    ctx_obj = ctx.ensure_object(dict)
    firefox_profile_path = check_type(ctx_obj["firefox_profile_path"], Path)
    job_title = check_type(ctx_obj["job_title"], str)

    offline_path = offline_path.resolve()

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
                if greenhouse_recruiting_job.title == job_title:
                    break
            else:
                raise RuntimeError("Could not find job by title")

            greenhouse_recruiting_job_applications = check_type(
                cache.get(
                    f"greenhouse_recruiting_job_applications:{greenhouse_recruiting_job.title}",
                    [],
                ),
                list[GreenhouseRecruitingJobApplication],
            )

            if not greenhouse_recruiting_job_applications:
                greenhouse_recruiting_job_applications = list(
                    greenhouse_recruiting_browser.all_job_applications(greenhouse_recruiting_job)
                )
                cache.set(
                    f"greenhouse_recruiting_job_applications:{greenhouse_recruiting_job.title}",
                    greenhouse_recruiting_job_applications,
                )

            for greenhouse_recruiting_job_application in greenhouse_recruiting_job_applications:

                application_url = urlparse(str(greenhouse_recruiting_job_application.target))
                application_path = PosixPath(application_url.path.strip("/"))
                application_id = str(parse_qs(application_url.query)["application_id"][0])

                offline_application_path = offline_path.joinpath(application_path) / application_id
                offline_application_metadata_path = offline_application_path / "metadata.json"

                if offline_application_path.exists():
                    continue

                greenhouse_recruiting_full_job_application = greenhouse_recruiting_browser.get_full_job_application(
                    greenhouse_recruiting_job_application
                )

                offline_application_path.mkdir(parents=True)

                copytree(str(download_path), str(offline_application_path), dirs_exist_ok=True)

                offline_application_metadata_path.write_text(
                    greenhouse_recruiting_full_job_application.model_dump_json(indent=2)
                )
