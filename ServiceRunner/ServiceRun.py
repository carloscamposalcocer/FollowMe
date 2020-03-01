import logging
import threading
from ServiceRunner.ConfigReader import ServiceConfig
from ServiceRunner.Workers import Worker, MultithreadWorker

logger = logging.getLogger(__name__)


class Service:
    def __init__(self):
        """

        :type config: ServiceConfig
        """
        logger.info(f"Init {self.__class__.__name__}")
        config = ServiceConfig.read_config(r"ServiceRunner/config.json")
        self.worker = MultithreadWorker(config)
        self.wait_lock = threading.Lock()
        self.wait_lock.acquire()
        self.worker.keep_running = False
        self.x = threading.Thread(target=self.run)
        self.x.start()

    def run(self):
        while True:
            self._wait()
            self._work()

    def start(self):
        logger.info(f"Starting {self.__class__.__name__}")
        if self.worker.keep_running:
            logger.info("Already running")
        else:
            self.worker.keep_running = True
            self.wait_lock.release()

    def stop(self):
        logger.info(f"Stopping {self.__class__.__name__}")
        if not self.worker.keep_running:
            logger.info("Already Stopped")
        else:
            self.wait_lock.acquire()
            self.worker.keep_running = False

    def close(self):
        logger.info(f"Closing {self.__class__.__name__}")
        self.stop()
        self.worker.close()

    def _work(self):
        self.worker.work()

    def _wait(self):
        logger.info("waiting Loop")
        self.wait_lock.acquire()
        self.wait_lock.release()


def main():
    service = Service()
    try:
        logger.info("starting grabbing")
        service.start()
        while True:
            logger.info("press enter to Stop")
            input()
            service.stop()
            logger.info("press enter to start")
            input()
            service.start()
    except (KeyboardInterrupt, EOFError):
        logger.info("Stopping Service")
        service.close()
    logger.info("Press any key to exit")


if __name__ == '__main__':
    main()
