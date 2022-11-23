import asyncio

import requests


def get_request():
    return requests.get("http://127.0.0.1:5000/hello").json()


if __name__ == "__main__":
    print(get_request())