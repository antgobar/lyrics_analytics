from lyrics_analytics.background.tasks import my_first_task


def route_a():
    return my_first_task("a", "b", c="c", d="d")


result = route_a()



