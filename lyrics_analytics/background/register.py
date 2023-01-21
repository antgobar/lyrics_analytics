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
    def __init__(self):
        self.registered_funcs = {}

    def register_func(self, func):
        self.registered_funcs[func.__name__] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.registered_funcs[func.__name__]["name"] = func.__name__
            self.registered_funcs[func.__name__]["func"] = func
            self.registered_funcs[func.__name__]["args"] = args
            self.registered_funcs[func.__name__]["kwargs"] = kwargs

            func_def = self.registered_funcs[func.__name__]
            no_func = {k: v for k, v in func_def.items() if k != "func"}
            send_message(func_def["name"], json.dumps(no_func))
            return {"status": f"function registered: {self.registered_funcs[func.__name__]}"}

        return wrapper

    def unregister_func(self, func):
        del self.registered_funcs[func.__name__]

    def run_task(self, func_name):
        func_def = self.registered_funcs[func_name]
        return func_def["func"](*func_def["args"], **func_def["kwargs"])
