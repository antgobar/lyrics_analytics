import json

from lyrics_analytics import Task

func_def = {
    "name": "find_artists",
    "args": ("metallica",)
}
Task.send_message("task_queue", json.dumps(func_def))

