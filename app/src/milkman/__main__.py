from concurrent.futures import ProcessPoolExecutor

# Part of the threads getting spawned by the main process are due to loguru - there's one for each sink
from .processes import GametickManager, FileObserver, FlagSubmitter


def main():
    """
    exploits = Exploits()
    log.info("Waiting for exploits to be loaded...")
    while not exploits:  # keep refreshing until there's an exploit
        time.sleep(3)
    else:
        log.success("Done")
    """

    executor = ProcessPoolExecutor(3)
    executor.submit(FileObserver)
    executor.submit(FlagSubmitter)
    executor.submit(GametickManager)

    executor.shutdown(wait=True, cancel_futures=False)  # waits for all tasks to finish
    exit(0)


if __name__ == "__main__":
    main()