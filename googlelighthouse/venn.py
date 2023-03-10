import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib_venn import venn2
import pandas as pd
import matplotlib as mpl


class Issue:
    def __init__(self, ty, code, message, context, selector):
        self.ty = ty
        self.code = code
        self.message = message
        self.context = context
        self.selector = selector

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Issue):
            return self.ty == o.ty and self.code == o.code and self.message == o.message and self.selector == o.selector
        else:
            return False

    def __repr__(self):
        return "Issue(%s, %s, %s, %s)" % (self.ty, self.code, self.message, self.selector)

    def __hash__(self):
        return hash(self.__repr__())


def read_(csv_file: str):
    data = pd.read_csv(csv_file)
    data.drop_duplicates(['type', 'code', 'message', 'selector'], inplace=True)
    issues = []
    for index, row in data.iterrows():
        issue = Issue(row['type'], row['code'], row['message'], row['context'], row['selector'])
        issues.append(issue)
    issues = set(issues)
    return issues


def draw_pie():
    with open("./report-gl.json", 'r') as f:
        report = json.load(f)
    for i in report['Web Pages']:
        df = []
        u = i['URL']
        title = ['Category in Mobile', 'Category in Desktop', 'Category in Intersection', 'Category in Union']
        m_cat = i['Category in Mobile']
        d_cat = i['Category in Desktop']
        i_cat = i['Category in Intersection']
        u_cat = i['Category in Union']
        y = []
        labels = []
        eachy = []
        label = []
        for k, v in m_cat.items():
            eachy.append(v)
            label.append(k.replace("cat.", ""))
        y.append(eachy)
        labels.append(label)
        eachy = []
        label = []
        for k, v in d_cat.items():
            eachy.append(v)
            label.append(k.replace("cat.", ""))
        y.append(eachy)
        labels.append(label)
        eachy = []
        label = []
        for k, v in i_cat.items():
            eachy.append(v)
            label.append(k.replace("cat.", ""))
        y.append(eachy)
        labels.append(label)
        eachy = []
        label = []
        for k, v in u_cat.items():
            eachy.append(v)
            label.append(k.replace("cat.", ""))
        y.append(eachy)
        labels.append(label)
        for ij in range(4):
            df.append((y[ij], labels[ij], title[ij]))
        fig, axs = plt.subplots(2, 2, figsize=(16, 9), dpi=200)
        for j in range(2):
            for k in range(2):
                axs[j, k].pie(df[j * 2 + k][0], labels=df[j * 2 + k][1], autopct='%.2f%%')
                axs[j, k].set_title(df[j * 2 + k][2])
        plt.suptitle(f"Categories of Issues in {u}")
        # plt.show()
        plt.savefig(f'./fig/{u.replace("://", "-").replace("/", "-").replace(".", "-")}.jpg')


def draw_venn():
    with open("../url_list.json", 'r') as f:
        url_list = json.load(f)
    dfs = []
    for u in url_list:
        s = u.replace("://", "-").replace("/", "-").replace(".", "-")
        df1 = read_(f"csv/{s}-desktop.csv")
        df2 = read_(f"csv/{s}-mobile.csv")
        if len(df1) == 0 and len(df2) == 0:
            continue
        dfs.append((df1, df2, u))
    plt.figure(0)
    fig = plt.figure(figsize=(16, 9), dpi=400)
    coordinates = [[(i, j) for j in range(3)] for i in range(3)]
    coordinates = [item for sublist in coordinates for item in sublist]
    axes = [plt.subplot2grid((3, 3), c) for c in coordinates][:-2]
    for ax, sample in zip(axes, dfs):
        set1 = set(sample[0])
        set2 = set(sample[1])
        v = venn2(subsets=[set1, set2], set_labels=('Desktop', 'Mobile'), ax=ax)
        try:
            v.get_patch_by_id('10').set_color('red')
            v.get_patch_by_id('01').set_color('blue')
            v.get_patch_by_id('10').set_edgecolor('none')
            v.get_patch_by_id('01').set_edgecolor('none')
            v.get_patch_by_id('10').set_alpha(0.4)
            v.get_patch_by_id('01').set_alpha(0.4)
            v.get_patch_by_id('11').set_color('#e098e1')
            v.get_patch_by_id('11').set_edgecolor('none')
            v.get_patch_by_id('11').set_alpha(0.4)
        except Exception:
            pass
        finally:
            ax.title.set_text(
                f"{sample[2]} IoU {round(len(set1.intersection(set2)) / len(set1.union(set2)), 2) if len(set1.union(set2)) != 0 else 0}")
    plt.show()


if __name__ == '__main__':
    draw_pie()
