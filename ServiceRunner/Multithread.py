import logging
from ServiceRunner.Workers import MultithreadWorker

logger = logging.getLogger(__name__)


def main():
    service = MultithreadWorker()
    service.start()


if __name__ == '__main__':
    main()
