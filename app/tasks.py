import uuid
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

Task = namedtuple('Task', ['id', 'fn', 'args', 'kwargs', 'priority'])

class TaskQueueManager:
    task_queue = queue.PriorityQueue()
    task_status = {}
    task_results = {}
    _executor = ThreadPoolExecutor(max_workers=4)

    @classmethod
    def get_all_tasks(cls):
        return [{"id": task_id, "status": status} for task_id, status in cls.task_status.items()]

    @classmethod
    def submit_task(cls, fn, *args, priority=10, **kwargs):
        task_id = str(uuid.uuid4())
        task = Task(task_id, fn, args, kwargs, priority)
        cls.task_status[task_id] = "queued"

        # Submit to executor directly
        future = cls._executor.submit(cls._run_task, task)
        future.add_done_callback(lambda f: cls._on_task_complete(task.id, f))

        return task_id

    @classmethod
    def _run_task(cls, task):
        cls.task_status[task.id] = "processing"
        return task.fn(*task.args, **task.kwargs)

    @classmethod
    def _on_task_complete(cls, task_id, future):
        try:
            result = future.result()
            cls.task_results[task_id] = result
            cls.task_status[task_id] = "completed"
        except Exception as e:
            cls.task_status[task.id] = "failed"
            cls.task_results[task_id] = str(e)

    @classmethod
    def get_status(cls, task_id):
        return cls.task_status.get(task_id, "not_found")

    @classmethod
    def get_result(cls, task_id):
        return cls.task_results.get(task_id, None)

    @classmethod
    def start(cls):
        # Executor is already started
        pass