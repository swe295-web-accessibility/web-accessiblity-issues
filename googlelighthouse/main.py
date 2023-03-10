import json
import time
from typing import Dict, List

import pandas as pd

import requests
import base64


def test_api(url: str, path: str, strategy="mobile"):
    while True:
        r = requests.get(
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=accessibility&strategy={strategy}",
            headers={
                'content-type': 'application/json',
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"})
        if not r.json().__contains__('error'):
            break
        time.sleep(2)
    with open(path, 'w') as f1:
        json.dump(r.json(), f1, indent=4)


def get_info_website(url: str):
    # print(f"===========================================" + "=" * (len(url) + 4))
    # print(f"|                                          " + " " * (len(url) + 3) + "|")
    # print(f"|   Summary of the accessibility issues in {url}   |")
    # print(f"|                                          " + " " * (len(url) + 3) + "|")
    # print(f"===========================================" + "=" * (len(url) + 4))
    file_name = url.replace(".", "-").replace("://", "-").replace("/", "-")
    # test_api(url, f'./metadata/{file_name}-mobile_meta.json')
    # test_api(url, f'./metadata/{file_name}-desktop_meta.json', 'desktop')
    # calculate_overall(f'./metadata/{file_name}-mobile_meta.json', f'./processed/{file_name}-mobile_processed.json')
    # calculate_overall(f'./metadata/{file_name}-desktop_meta.json', f'./processed/{file_name}-desktop_processed.json')
    # # # type,code,message,context,selector
    # print("Storing results as csv files")
    # json2csv(f'./processed/{file_name}-desktop_processed.json', f'./csv/{file_name}-desktop.csv')
    # json2csv(f'./processed/{file_name}-mobile_processed.json', f'./csv/{file_name}-mobile.csv')
    compare_mobile_desktop(f'./csv/{file_name}-mobile.csv', f'./csv/{file_name}-desktop.csv', url)


def json2csv(file_path: str, csv_file: str):
    df_data = {
        "type": [],
        "code": [],
        "message": [],
        "context": [],
        "selector": [],
        "category": []
    }
    problem = json.load(open(file_path, 'r'))['problem']
    for k, v in problem.items():
        impact = k
        for k1, v1 in v.items():
            tags: List[str] = v1['details']['debugData']['tags']
            except_set = {"ACT", "wcag2a", "wcag2aa"}
            code = ','.join(
                c for c in tags if not (c.startswith("cat") or c.startswith("section508") or c in except_set))
            cat = "".join(c for c in tags if c.startswith("cat"))
            items: List = v1['details']['items']
            for it in items:
                if it.__contains__('node'):
                    df_data['type'].append(impact)
                    df_data['code'].append(code)
                    df_data['message'].append(it['node']['explanation'])
                    df_data['context'].append(it['node']['snippet'])
                    df_data['selector'].append(it['node']['selector'])
                    df_data['category'].append(cat)
                else:
                    ittems = it['subItems']['items']
                    for i in ittems:
                        df_data['type'].append(impact)
                        df_data['code'].append(code)
                        df_data['message'].append(i['relatedNode']['nodeLabel'])
                        df_data['context'].append(i['relatedNode']['snippet'])
                        df_data['selector'].append(it['relatedNode']['selector'])
                        df_data['category'].append(cat)

    df = pd.DataFrame(df_data)
    df.drop_duplicates(subset=['type', 'code', 'message', 'context'], inplace=True)
    df.to_csv(csv_file, index=False)


def calculate_overall(path: str, store_path: str):
    with open(path, 'r') as f:
        tmp = json.load(f)
    audits = tmp['lighthouseResult']['audits']
    score = float(tmp['lighthouseResult']['categories']["accessibility"]['score'])
    audit_refs: List[Dict] = tmp['lighthouseResult']['categories']["accessibility"]['auditRefs']
    audit_refs_dict = {}
    for a in audit_refs:
        audit_refs_dict[a['id']] = {'weight': a['weight'], 'group': a['group'] if a.__contains__('group') else None}
    not_applicable = {}
    manual = {}
    binary_0 = {}
    fail = 0
    binary_1 = {}
    error = {}

    for k, v in audits.items():
        # notApplicable.add(v['scoreDisplayMode']) {'notApplicable', 'informative', 'binary', 'manual'}
        if v['scoreDisplayMode'] == 'notApplicable':
            del v['scoreDisplayMode']
            del v['score']
            v['weight'] = audit_refs_dict[v['id']]['weight']
            v['group'] = audit_refs_dict[v['id']]['group']
            not_applicable[k] = v
        elif k == 'full-page-screenshot' and v['scoreDisplayMode'] == 'informative':
            data = None
            for k1, v1 in v.items():
                if k1 == 'details':
                    data = v1['screenshot']['data'].split("base64,")[1]
                    break
            with open(f"{store_path.replace('json', 'jpg').replace('processed', 'screenshot')}", 'wb') as fp:
                fp.write(base64_to_image(data))
        elif v['scoreDisplayMode'] == "SCORE_DISPLAY_MODE_UNSPECIFIED":
            raise Exception("score unspecified")
        elif v['scoreDisplayMode'] == 'binary':
            if v['score'] == 0:
                impact = v['details']['debugData']['impact']
                del v['scoreDisplayMode']
                del v['score']
                v['weight'] = audit_refs_dict[v['id']]['weight']
                v['group'] = audit_refs_dict[v['id']]['group']
                if not binary_0.__contains__(impact):
                    binary_0[impact] = {}
                binary_0[impact][k] = v
                fail += 1
            elif v['score'] == 1:
                del v['scoreDisplayMode']
                del v['score']
                v['weight'] = audit_refs_dict[v['id']]['weight']
                v['group'] = audit_refs_dict[v['id']]['group']
                binary_1[k] = v
        elif v['scoreDisplayMode'] == 'error':
            del v['scoreDisplayMode']
            del v['score']
            v['weight'] = audit_refs_dict[v['id']]['weight']
            v['group'] = audit_refs_dict[v['id']]['group']
            error[k] = v
        elif v['scoreDisplayMode'] == 'manual':
            del v['scoreDisplayMode']
            del v['score']
            v['weight'] = audit_refs_dict[v['id']]['weight']
            v['group'] = audit_refs_dict[v['id']]['group']
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
    print(f"{tmp['lighthouseResult']['configSettings']['formFactor']}: ")
    print(f"\t\tPass  : {len(binary_1)}")
    print(f"\t\tFail  : {fail}")
    print(f"\t\tManual: {len(manual)}")
    with open(store_path, 'w') as fp:
        json.dump(meta_data, fp, indent=4)


def path2XPath(pth_str: str):
    split_str = pth_str.split(",")
    xpath = ""
    for i in range(0, len(split_str), 2):
        xpath = f'{xpath}/{split_str[i + 1]}[{split_str[i]}]'
    return xpath.lower()


def compare_mobile_desktop(mobile: str, desktop: str, url: str):
    df1 = pd.read_csv(mobile)
    df2 = pd.read_csv(desktop)
    df1.drop_duplicates(['type', 'code', 'message', 'selector', 'category'], inplace=True)
    cat1 = df1['category'].value_counts().to_dict()
    df2.drop_duplicates(['type', 'code', 'message', 'selector', 'category'], inplace=True)
    cat2 = df2['category'].value_counts().to_dict()
    df_inter = pd.merge(df1, df2, how='inner', on=['type', 'code', 'message', 'selector', 'category'])
    cat_inter = df_inter['category'].value_counts().to_dict()
    df_union = pd.concat([df1, df2], ignore_index=True)
    df_union.drop_duplicates(['type', 'code', 'message', 'selector', 'category'], inplace=True)
    cat_union = df_union['category'].value_counts().to_dict()
    print(f"====================================================")
    print(f"|                                                  |")
    print(f"|   Comparing results between Desktop and Mobile   |")
    print(f"|                                                  |")
    print(f"====================================================")
    report['Number of Desktop issues'] = df2.shape[0]
    report['Number of Mobile issues'] = df1.shape[0]
    print(f"The number of the intersection: {df_inter.shape[0]}")
    report['Number of Intersection issues'] = df_inter.shape[0]
    df_inter.to_csv(f"./csv/{url.replace('://', '-').replace('/', '-').replace('.', '-')}-intersection.csv",
                    index=False)
    print(f"The number of the union: {df_union.shape[0]}")
    report['Number of Union issues'] = df_union.shape[0]
    df_union.to_csv(f"./csv/{url.replace('://', '-').replace('/', '-').replace('.', '-')}-union.csv", index=False)
    print(f"The number of the problems that are unique in mobile: {df1.shape[0] - df_inter.shape[0]}")
    report['Number of issues that appear only on Mobile'] = df1.shape[0] - df_inter.shape[0]
    print(f"The number of the problems that are unique in desktop: {df2.shape[0] - df_inter.shape[0]}")
    report['Number of issues that appear only on Desktop'] = df2.shape[0] - df_inter.shape[0]
    report['Intersection over Union'] = 0 if df_union.shape[0] == 0 else df_inter.shape[0] * 1.0 / df_union.shape[0]
    report['Category in Mobile'] = cat1
    report['Category in Desktop'] = cat2
    report['Category in Intersection'] = cat_inter
    report['Category in Union'] = cat_union
    mob = pd.concat([df1, df_inter], ignore_index=True).drop_duplicates(['type', 'code', 'message', 'selector'],
                                                                        keep=False)
    desk = pd.concat([df2, df_inter], ignore_index=True).drop_duplicates(['type', 'code', 'message', 'selector'],
                                                                         keep=False)
    mob.to_csv(f"./csv/{url.replace('://', '-').replace('/', '-').replace('.', '-')}-mob-unique.csv", index=False)
    desk.to_csv(f"./csv/{url.replace('://', '-').replace('/', '-').replace('.', '-')}-desk-unique.csv", index=False)


def base64_to_image(base64_string: str):
    data = base64.b64decode(base64_string)
    return data


if __name__ == '__main__':
    reports = []
    with open("../url_list.json", 'r') as f:
        url_list = json.load(f)
    for u in url_list:
        report = {
            "URL": u,
            "Number of Desktop issues": 0,
            "Number of Mobile issues": 0,
            "Number of Intersection issues": 0,
            "Number of Union issues": 0,
            "Number of issues that appear only on Desktop": 0,
            "Number of issues that appear only on Mobile": 0,
            "Intersection over Union": 0,
            "Category in Mobile": {},
            "Category in Desktop": {},
            "Category in Intersection": {},
            "Category in Union": {},
        }
        get_info_website(u)
        reports.append(report)
    json.dump({"Web Pages": reports}, open("./report-gl.json", 'w'), indent=4)
