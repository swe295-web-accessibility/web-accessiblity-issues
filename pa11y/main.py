import subprocess


def main(url: str, path: str):
    try:
        subprocess.check_call("pa11y")
    except subprocess.CalledProcessError:
        subprocess.run("npm install -g pa11y")
    subprocess.run(f"pa11y --reporter csv {url} > {path}", shell=True)


if __name__ == '__main__':
    main("https://nytimes.com", "./nytimes_pa11y.csv")
