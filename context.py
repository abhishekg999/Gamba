import threading

class ThreadContextManager:
    """
    Context manager for background threads (maybe processes)

    On enter, takes functions to run in separate threads. 
    On exit, waits for all threads to finish.
    """

    def __init__(self, *runners):
        self.runners = runners

    def __enter__(self):
        self.threads = []
        for runner in self.runners:
            t = threading.Thread(target=runner)
            t.daemon = True
            self.threads.append(t)

        for thread in self.threads:
            thread.start()

        return self.threads

    def __exit__(self, exc_type, exc_value, traceback):
        for thread in self.threads:
            thread.join()

