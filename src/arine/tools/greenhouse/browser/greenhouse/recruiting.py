import json
from pathlib import Path
from time import sleep
from typing import Iterator

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from typeguard import check_type, typechecked

from arine.tools.greenhouse.models.greenhouse.recruiting.jobs import (
    GreenhouseRecruitingFullJobApplication,
    GreenhouseRecruitingJob,
    GreenhouseRecruitingJobApplication,
)


class GreenHouseRecruitingBrowser:
    @typechecked
    def __init__(self, profile_path: Path, download_path: Path):

        self.download_path = download_path

        options = FirefoxOptions()
        options.add_argument("--no-remote")
        options.add_argument("--profile")
        options.add_argument(str(profile_path))

        # 2 = Use custom download location
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(download_path.resolve()))
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf,application/octet-stream,application/vnd.ms-excel",
        )
        options.set_preference("pdfjs.disabled", True)  # Disable built-in PDF viewer

        service = FirefoxService("/opt/homebrew/bin/geckodriver")

        self.webdriver = FirefoxWebDriver(options=options, service=service)

        self.logged_in = False

    @typechecked
    def wait_for_page_load(self, timeout=10, /):
        checks = []

        def check_readystate_complete() -> bool:
            try:
                return WebDriverWait(self.webdriver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete",
                )
            except Exception:
                return False

        for _ in range(20):
            check = check_readystate_complete()
            checks.append(check)
            if len(checks) > 3:
                if all(checks[-3:]):
                    return True
            sleep(0.5)

        return False

    def login(self):
        if not self.logged_in:
            self.webdriver.get("https://app4.greenhouse.io/users/auth/google_oauth2")
            self.wait_for_page_load()
            if self.webdriver.title != "My Dashboard | Greenhouse Recruiting":
                raise RuntimeError("Dashboard page not appear to be valid")
            self.logged_in = True

    @typechecked
    def all_jobs(self) -> Iterator[GreenhouseRecruitingJob]:
        self.login()
        self.webdriver.get("https://app4.greenhouse.io/alljobs")

        # <td class="job-cell job-name">
        #    <a title="Agency - ... (...) (...)" class="target" href="/sdash/4646912004">
        #    ...
        #    </a>
        #    ...
        # </td>

        td_elements = WebDriverWait(self.webdriver, 10).until(
            expected_conditions.presence_of_all_elements_located(
                (By.XPATH, "//td[contains(@class, 'job-cell') and contains(@class, 'job-name')]")
            )
        )

        if self.webdriver.title != "All Jobs | Greenhouse Recruiting":
            raise RuntimeError("All jobs page does not appear to be valid")

        for td in td_elements:
            a_element = td.find_element(By.CLASS_NAME, "target")
            yield GreenhouseRecruitingJob.model_validate(
                {
                    "target": a_element.get_attribute("href"),
                    "title": a_element.get_attribute("title"),
                }
            )

    def all_job_applications(
        self, greenhouse_recruiting_job: GreenhouseRecruitingJob, /
    ) -> Iterator[GreenhouseRecruitingJobApplication]:
        self.login()
        self.webdriver.get(str(greenhouse_recruiting_job.target))
        self.wait_for_page_load()

        a_element = WebDriverWait(self.webdriver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//a[contains(@class, 'link_list__StyledLink')]" "[.//p[contains(text(), 'Candidates')]]")
            )
        )

        job_candidates_url = a_element.get_attribute("href")

        if not isinstance(job_candidates_url, str):
            raise RuntimeError("Job candidates URL does not appear to be valid")

        self.webdriver.get(job_candidates_url)

        for _ in range(100):  # limit 100 pages
            self.wait_for_page_load()

            try:
                a_elements = self.webdriver.find_elements(By.XPATH, "//a[starts-with(@href, '/people')]")
            except Exception:
                a_elements = []

            for a_element in a_elements:
                target = a_element.get_attribute("href")
                text = a_element.text

                if isinstance(target, str):
                    if "application_id=" not in target:
                        continue

                yield GreenhouseRecruitingJobApplication.model_validate({"target": target, "name": text})

            try:
                a_element = self.webdriver.find_element(By.XPATH, "//a[contains(@class, 'next_page')]")
            except Exception:
                break

            self.webdriver.get(str(a_element.get_attribute("href")))

    def get_full_job_application(
        self, greenhouse_recruiting_job_application: GreenhouseRecruitingJobApplication, /
    ) -> GreenhouseRecruitingFullJobApplication:
        self.login()
        self.webdriver.get(str(greenhouse_recruiting_job_application.target))
        self.wait_for_page_load()

        div_element = self.webdriver.find_element(
            By.XPATH, "//div[@data-react-class='CandidateProfileRedesign.CandidateProfile']"
        )

        candidate_profile_json = div_element.get_attribute("data-react-props")

        if not isinstance(candidate_profile_json, str):
            raise RuntimeError("Idk.. getting tired")

        candidate_profile_obj = check_type(json.loads(candidate_profile_json), dict)

        candidate_profile_header_obj = check_type(candidate_profile_obj.get("header", {}), dict)
        candidate_profile_resume_obj = check_type(candidate_profile_header_obj.get("resume", {}), dict)
        candidate_profile_resume_download_url = check_type(candidate_profile_resume_obj.get("downloadUrl"), str)

        resume_path = self.download_path / "resume.pdf"

        with resume_path.open("+wb") as fd:
            response = requests.get(candidate_profile_resume_download_url)  # noqa: S113
            for chunk in response.iter_content(chunk_size=65536):
                fd.write(chunk)

        return GreenhouseRecruitingFullJobApplication(
            target=greenhouse_recruiting_job_application.target,
            name=greenhouse_recruiting_job_application.name,
            resume=resume_path,
        )

    def close(self):
        self.webdriver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
