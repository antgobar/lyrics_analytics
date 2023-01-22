import functools
import json

from lyrics_analytics.background.mq_connection import send_message


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TaskRegister(metaclass=Singleton):
    _registered_tasks = {}

    @classmethod
    def register_task(cls, func):
        cls._registered_tasks[func.__name__] = {}
        cls._registered_tasks[func.__name__]["func"] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_def = {
                "name": cls._registered_tasks[func.__name__],
                "args": args,
                "kwargs": kwargs
            }
            send_message("task_queue", json.dumps(func_def))
            return {"status": f"function registered: {cls._registered_tasks[func.__name__]}"}

        return wrapper

    @classmethod
    def unregister_func(cls, func):
        del cls._registered_tasks[func.__name__]

    @classmethod
    def run_task(cls, func_name, *args, **kwargs):
        func = cls._registered_tasks[func_name]
        return func(*args, **kwargs)
