from worker.core.queue_worker import LazyLectureQueueWorker
from worker.core.settings import settings

if __name__ == "__main__":
    worker = LazyLectureQueueWorker(settings)
    worker.start()
