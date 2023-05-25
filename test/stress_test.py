from functools import wraps

import grequests
import requests


BASE_URL = "http://localhost:5000/"


def full_route(callback):
    @wraps(callback)
    def inner(*args, **kwargs):
        return BASE_URL + callback(*args, **kwargs)

    return inner


@full_route
def login(username, password):
    return f"login?username={username}&password={password}"


@full_route
def me(token):
    return f"me?token={token}"


@full_route
def lower(token, bet, target):
    return f"lower?token={token}&bet={bet}&target={target}"

@full_route
def beg(token):
    return f"beg?token={token}"


def get(url, timeout=5, *args, **kwargs):
    response = requests.get(url, timeout=timeout, *args, **kwargs)
    data = response.json()

    return data


if __name__ == "__main__":
    username = "admin"
    password = "password"

    print("Beginning tests...")
    data = get(login(username, password))

    print(data)
    token = data["token"]
    print(token)

    data = get(me(token))
    old_data = data
    print(data)

    current_money = float(data['money'])

    NUM_REQUESTS = 5000
    POOL = 5000

    rs = (grequests.get(beg(token)) for _ in range(NUM_REQUESTS))
    responses = grequests.imap(rs, size=POOL)

    for response in responses:
        print(response.json())

    data = get(me(token))
    print(old_data)
    print(data)
    assert float(data['money']) == current_money + NUM_REQUESTS*100
