#!/usr/local/bin/node

const pa11y = require('pa11y');
const csv = require('pa11y/lib/reporters/csv');
const fs = require('fs');

const iphone12PrEnv = {
    viewport: {
        width: 390,
        height: 844,
        isMobile: true
    }
}

const desktopEnv = {
    viewport: {
        width: 1280,
        height: 1024,
        isMobile: false
    }
}
const urlToFileName = (url) => {
    return url.replaceAll("://", "-").replaceAll("/", "-").replaceAll(".", "-");
}

async function runPa11y(url, isMobile) {
    try {
        const replacedURL = urlToFileName(url);
        var screenshotPath = "";
        var csvFilePath = "";
        var viewport = null;
        if (isMobile) {
            let name = `${replacedURL}-mobile`
            screenshotPath = 'screenshot/' + name + '.png';
            csvFilePath = 'csv/' + name + '.csv';
            viewport = iphone12PrEnv.viewport;
        } else {
            let name = `${replacedURL}-desktop`
            screenshotPath = 'screenshot/' + name + '.png';
            csvFilePath = 'csv/' + name + '.csv';
            viewport = desktopEnv.viewport;
        }

        const results = await pa11y(url, {
            viewport: viewport,
            screenCapture: screenshotPath,
            includeWarnings: true,
            log: {
                debug: console.log,
                error: console.error,
                info: console.info
            }
        });

        results.issues.sort((a, b) => a.typeCode - b.typeCode);
        const csvResult = await csv.results(results);

        fs.writeFile(csvFilePath, csvResult, err => {
            if (err) {
              console.error(err);
            }
          });
        return results
    } catch (error) {
        console.log(error);
        return null
    }
}

const intersect = (arr1, arr2) => {
    let f = arr1.filter(item1 => {
        let filter2 = arr2.filter(item2 => {
            return item1.type == item2.type && item1.code == item2.code && item1.context == item2.context
        })
        return filter2.length >= 1
    });

    const map = new Map();

    for (item of f) {
        map.set(`${item.type}${item.code}${item.context}`, item);
    }
    
    return Array.from(map.values());
};

const union = (arr1, arr2) => {
    let intersection = intersect(arr1, arr2);

    let onlyInArr1 = arr1.filter(item1 => {
         let filter2 = intersection.filter(item2 => {
            return item1.code == item2.code && item1.context == item2.context
        })
        return filter2.length == 0;
    });
    return onlyInArr1.concat(arr2);
};

async function writeIOUCSV(targetPageURL, isIntersection, result) {

    result.issues.sort((a, b) => a.typeCode - b.typeCode);
    const csvResult = await csv.results(result);
    const replacedURL = urlToFileName(url);
    var filePath = ""
    if (isIntersection) {
        filePath = `csv/${replacedURL}-intersection.csv`
    } else {
        filePath = `csv/${replacedURL}-union.csv`
    }

    fs.writeFile(filePath, csvResult, err => {
        if (err) {
            console.error(err);
        }
    });
}

async function run(url) {
    mobileResult = await runPa11y(url, true);
    desktopResult = await runPa11y(url, false);

    let intersectionResult = Object.assign({}, mobileResult);
    let unionResult = Object.assign({}, mobileResult);
    intersectionResult.issues = intersect(mobileResult.issues, desktopResult.issues);
    unionResult.issues = union(mobileResult.issues, desktopResult.issues);

    await writeIOUCSV(url, true, intersectionResult);
    await writeIOUCSV(url, false, unionResult);

    return [url, desktopResult, mobileResult, intersectionResult, unionResult];
}

class AnalysisResultContainer {
    constructor(results) {
        this.results = results
    }

    metadata() {
        return {
            "Desktop": desktopEnv,
            "Mobile": iphone12PrEnv,
            "Included Type": "Error, Warning"
        }
    }

    jsonReport() {
        var desc = []
        for (res of this.results) {
            desc.push(res.description());
        }
        let container = {
            "Metadata": this.metadata(),
            "Web Pages": desc
        }
        return JSON.stringify(container, null, 4);
    }
}

class AnalysisResult {
    constructor(url, desktop, mobile, intersection, union) {
        this.url = url
        this.desktop = desktop
        this.mobile = mobile
        this.intersection = intersection
        this.union = union
    }

    description() {
        return {
            "URL": this.url,
            "Number of Desktop issues" : this.desktop.issues.length,
            "Number of Mobile issues" : this.mobile.issues.length,
            "Number of Intersection issues" : this.intersection.issues.length,
            "Number of Union issues" : this.union.issues.length,
            "Number of issues that appear only on Desktop" : this.desktop.issues.length - this.intersection.issues.length,
            "Number of issues that appear only on Mobile" : this.mobile.issues.length - this.intersection.issues.length,
            "Intersection over Union" : this.intersectionOverUnion()
        }
    }

    intersectionOverUnion() {
        return this.intersection.issues.length / this.union.issues.length;
    }
}

// Usage
async function main() {
    targetURLs = [
        "https://usability.yale.edu/web-accessibility",
        "https://samsung.com/",
        "https://www.ikea.com",
        "https://www.geeksforgeeks.org/",
        "https://www.traderjoes.com/home",
        "https://developer.mozilla.org/en-US/",
        "https://www.etsy.com/",
        "https://www.ics.uci.edu/",
        "https://www.costco.com/",
        "https://www.wikipedia.org/"
    ]
    
    analysisResults = []
    for (url of targetURLs) {
        res = await run(url);
        analysisRes = new AnalysisResult(res[0], res[1], res[2], res[3], res[4]);
        analysisResults.push(analysisRes);
    }
    
    for (res of analysisResults) {
        console.log(res.description());
    } 

    resultContainer = new AnalysisResultContainer(analysisResults);
    fs.writeFile("./report.json", resultContainer.jsonReport(), err => {
        if (err) {
            console.error(err);
        }
    });

    fs.writeFile("./pa11yResult.json", JSON.stringify(resultContainer, null, 4), err => {
        if (err) {
            console.error(err);
        }
    });
}
main();