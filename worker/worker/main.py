import asyncio

from worker.core.worker import LazyLectureWorker
from worker.core.settings import settings


async def main():
    worker = LazyLectureWorker(settings)
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
