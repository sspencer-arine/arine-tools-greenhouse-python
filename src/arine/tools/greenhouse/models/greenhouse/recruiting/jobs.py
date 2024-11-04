from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel


class GreenhouseRecruitingJob(BaseModel):
    target: AnyHttpUrl
    title: str


class GreenhouseRecruitingJobApplication(BaseModel):
    target: AnyHttpUrl
    name: str


class GreenhouseRecruitingFullJobApplication(BaseModel):
    target: AnyHttpUrl
    name: str
    resume: Path
