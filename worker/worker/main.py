import asyncio

from worker.core.worker import LazyLectureWorker
from worker.core.settings import Settings


async def main():
    settings = Settings()
    worker = LazyLectureWorker(settings)
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
