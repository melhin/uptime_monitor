from typing import List, Tuple

from pydantic import BaseModel


class AvailableJobs(BaseModel):
    site_id: int
    url: str
    job_id: int


class JobDB:
    def __init__(self, cursor) -> None:
        self.cursor = cursor

    async def get_available_jobs(self, limit: int = 10) -> AvailableJobs:
        """Our small job queue using basic sql locks with for update
        and skip locked.
        """
        select_statement = (
            "select sc.id, sc.url, j.id  from jobs j inner join site_config sc "
            "on j.site_config_id=sc.id order by j.created_at desc "
            "for update of sc skip locked limit %s"
        )
        await self.cursor.execute(select_statement, (limit,))

        available_jobs = []
        for site_id, url, job_id in await self.cursor.fetchall():
            available_jobs.append(
                AvailableJobs(
                    site_id=site_id,
                    url=url,
                    job_id=job_id,
                )
            )
        return available_jobs

    async def delete_jobs_with_id(self, job_ids: List[Tuple[int]]):
        delete_statement = "delete from jobs where id in %s"
        await self.cursor.execute(delete_statement, (tuple(job_ids),))
