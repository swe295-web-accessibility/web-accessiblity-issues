from matplotlib import pyplot as plt
from matplotlib_venn import venn2, venn2_circles
import numpy as np
import json
import random

class Issue:
    def __init__(self, code, type, typeCode, message, context, selector, runnerExtras) -> None:
        self.code = code
        self.type = type
        self.typeCode = typeCode
        self.message = message
        self.context = context
        self.selector = selector
        self.runnerExtras = runnerExtras
    
    def __repr__(self):
        return "Issue(%s, %s)" % (self.code, self.context)

    def __eq__(self, other):
        if isinstance(other, Issue):
            return ((self.code == other.code) and (self.context == other.context))
        else:
            return False
        
    def __hash__(self):
        return hash(self.__repr__())

class Environment: 
    def __init__(self, documentTitle, pageUrl, issues) -> None:
        self.documentTitle = documentTitle
        self.pageUrl = pageUrl
        self.issues = [Issue(code=i["code"], type=i["type"], typeCode=i["typeCode"], message=i["message"], context=i["context"], selector=i["selector"], runnerExtras=i["runnerExtras"]) for i in issues]
        
class Result:
    def __init__(self, url, desktops, mobiles, intersections, union) -> None:
        self.url = url
        self.desktops = Environment(desktops["documentTitle"], desktops["pageUrl"], desktops["issues"])
        self.mobiles = Environment(mobiles["documentTitle"], mobiles["pageUrl"], mobiles["issues"])
        self.intersections = Environment(intersections["documentTitle"], intersections["pageUrl"], intersections["issues"])
        self.union = Environment(union["documentTitle"], union["pageUrl"], union["issues"])

def plotVennDiagram(n, results):
    samples = random.sample(results, n)

    plt.figure(0)
    fig = plt.figure(0)
    coordinates = [[(i, j) for j in range(3)] for i in range(3)]
    coordinates = [item for sublist in coordinates for item in sublist]

    axes = [plt.subplot2grid((3,3), c) for c in coordinates]

    for ax, sample in zip(axes, samples):
        # Venn Diagram Set data
        set1 = set(sample.desktops.issues)
        set2 = set(sample.mobiles.issues)
        v = venn2(subsets=[set1, set2], set_labels=('Desktop', 'Mobile'), ax=ax)

        # Design
        v.get_patch_by_id('10').set_color('red')
        v.get_patch_by_id('01').set_color('blue')
        v.get_patch_by_id('10').set_edgecolor('none')
        v.get_patch_by_id('01').set_edgecolor('none')
        v.get_patch_by_id('10').set_alpha(0.4)
        v.get_patch_by_id('01').set_alpha(0.4)
        v.get_patch_by_id('11').set_color('#e098e1')
        v.get_patch_by_id('11').set_edgecolor('none')
        v.get_patch_by_id('11').set_alpha(0.4)
        ax.title.set_text(f"{sample.url} IoU {round(len(sample.intersections.issues) / len(sample.union.issues), 2)}")

    plt.show()

f = open('pa11yResult.json')
data = json.load(f)

results = []
for obj in data['results']:
    res = Result(url = obj["url"], desktops=obj["desktop"], mobiles=obj["mobile"], intersections=obj["intersection"], union=obj["union"])
    results.append(res)
f.close()

plotVennDiagram(n = 9, results = results)
