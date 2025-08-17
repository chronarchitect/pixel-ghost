import uuid
import multiprocessing
import queue
import threading
import time
from collections import namedtuple

Task = namedtuple('Task', ['id', 'fn', 'args', 'kwargs', 'priority'])

class TaskQueueManager:
    task_queue = queue.PriorityQueue()
    task_status = {}
    task_results = {}
    num_workers = multiprocessing.cpu_count()

    @classmethod
    def submit_task(cls, fn, *args, priority=10, **kwargs):
        task_id = str(uuid.uuid4())
        task = Task(task_id, fn, args, kwargs, priority)
        cls.task_status[task_id] = "queued"
        cls.task_queue.put((priority, task))
        return task_id

    @classmethod
    def get_status(cls, task_id):
        return cls.task_status.get(task_id, "not_found")

    @classmethod
    def get_result(cls, task_id):
        return cls.task_results.get(task_id, None)

    @classmethod
    def _worker(cls):
        while True:
            try:
                _, task = cls.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            cls.task_status[task.id] = "processing"

            try:
                with multiprocessing.Pool(1) as pool:
                    result = pool.apply(task.fn, task.args, task.kwargs)
            except Exception as e:
                cls.task_status[task.id] = "failed"
                cls.task_results[task.id] = str(e)
            else:
                cls.task_status[task.id] = "completed"
                cls.task_results[task.id] = result

            cls.task_queue.task_done()

    @classmethod
    def start(cls):
        for _ in range(cls.num_workers):
            threading.Thread(target=cls._worker, daemon=True).start()