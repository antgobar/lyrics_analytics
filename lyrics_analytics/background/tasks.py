from lyrics_analytics.background.task import TaskRegister


task = TaskRegister().register_task


@task
def my_first_task(*args, **kwargs):
    print(args, kwargs)
    return args, kwargs
