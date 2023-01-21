from lyrics_analytics.background.register import TaskRegister

register = TaskRegister()
task = register.register_func


@task
def my_first_task(*args, **kwargs):
    return args, kwargs
