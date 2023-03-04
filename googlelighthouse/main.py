import json

import requests
import base64


def test_api(url: str, path: str, strategy="mobile"):
    r = requests.get(
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=accessibility&strategy={strategy}",
        headers={
            'content-type': 'application/json',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"})
    with open(path, 'w') as f:
        json.dump(r.json(), f, indent=4)


def calculate_overall(path: str):
    with open(path, 'r') as f:
        tmp = json.load(f)
    audits = tmp['lighthouseResult']['audits']
    score = float(tmp['lighthouseResult']['categories']["accessibility"]['score'])
    not_applicable = {}
    manual = {}
    binary_0 = {}
    binary_1 = {}
    error = {}

    for k, v in audits.items():
        # notApplicable.add(v['scoreDisplayMode']) {'notApplicable', 'informative', 'binary', 'manual'}
        if v['scoreDisplayMode'] == 'notApplicable':
            del v['scoreDisplayMode']
            del v['score']
            not_applicable[k] = v
        elif k == 'full-page-screenshot' and v['scoreDisplayMode'] == 'informative':
            data = None
            for k1, v1 in v.items():
                if k1 == 'details':
                    data = v1['screenshot']['data'].split("base64,")[1]
                    break
            with open(
                    f"./{hash(tmp['id'])}_{tmp['lighthouseResult']['configSettings']['emulatedFormFactor']}_screenshot.jpg",
                    'wb') as fp:
                fp.write(base64_to_image(data))
        elif v['scoreDisplayMode'] == "SCORE_DISPLAY_MODE_UNSPECIFIED":
            raise Exception("score unspecified")
        elif v['scoreDisplayMode'] == 'binary':
            if v['score'] == 0:
                impact = v['details']['debugData']['impact']
                del v['scoreDisplayMode']
                del v['score']
                if not binary_0.__contains__(impact):
                    binary_0[impact] = {}
                binary_0[impact][k] = v
            elif v['score'] == 1:
                del v['scoreDisplayMode']
                del v['score']
                binary_1[k] = v
        elif v['scoreDisplayMode'] == 'error':
            del v['scoreDisplayMode']
            del v['score']
            error[k] = v
        elif v['scoreDisplayMode'] == 'manual':
            del v['scoreDisplayMode']
            del v['score']
            manual[k] = v
        elif v['scoreDisplayMode'] == 'numeric':
            print('====numeric===')
        else:
            raise Exception("Not handled")

    meta_data = {
        "score": score,  # total score
        "problem": binary_0,  # audit problem
        "pass": binary_1,  # audit pass
        "manual": manual,
        "not_applicable": not_applicable
    }
    with open(f"./{hash(tmp['id'])}_{tmp['lighthouseResult']['configSettings']['emulatedFormFactor']}_meta_data.json",
              'w') as fp:
        json.dump(meta_data, fp, indent=4)


def compare_mobile_desktop(pth1: str, pth2: str):
    json1 = json.load(open(pth1))
    json2 = json.load(open(pth2))
    problem1 = json1['problem']
    problem2 = json2['problem']
    problem1_ = {}
    problem2_ = {}
    for k, v in problem1.items():
        for k1, v1 in v.items():
            problem1_[k1] = v1
    for k, v in problem2.items():
        for k1, v1 in v.items():
            problem2_[k1] = v1
    print(sorted(problem1_.items()))
    print(sorted(problem2_.items()))


def base64_to_image(base64_string: str):
    data = base64.b64decode(base64_string)
    return data


if __name__ == '__main__':
    # calculate_overall(r'D:\Projects\web-accessiblity-issues\googlelighthouse\adobe_google_lh_mobile.json')
    # calculate_overall(r'D:\Projects\web-accessiblity-issues\googlelighthouse\adobe_google_lh_desktop.json')
    # test_api("https://www.adobe.com/", "./adobe_google_lh_mobile.json")
    # test_api("https://www.adobe.com/", "./adobe_google_lh_desktop.json", "desktop")
    compare_mobile_desktop("./5662459776350690832_desktop_meta_data.json",
                           "./5662459776350690832_mobile_meta_data.json")
