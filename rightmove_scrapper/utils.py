import random


def proxy_rotator():
    with open('proxies.txt', 'r') as file:
        content = file.read().split("\n")

    proxy_url_list = []
    for proxy_ip in content:
        if proxy_ip == "":
            continue
        else:
            proxy_url_list.append(f"http://{proxy_ip}")
    return random.choice(proxy_url_list)



