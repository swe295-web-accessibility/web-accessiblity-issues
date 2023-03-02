import json

import requests


def test_api(url: str, path: str):
    payload = {"act": "true",
               "url": url,
               "wcag": "true"
               }
    r = requests.post("http://qualweb.di.fc.ul.pt/api/app/url/", json=payload, headers={
        'content-type': 'application/json',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"})
    with open(path, 'a') as f:
        json.dump(r.json(), f, indent=4)


if __name__ == '__main__':
    test_api("https://www.nytimes.com/", "./nytimes_qualweb.json")
