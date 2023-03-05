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
            includeNotices: true,
            includeWarnings: true,
            wait: 1000,
            log: {
                debug: console.log,
                error: console.error,
                info: console.info
            }
        })
        
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
    let filter = arr1.filter(item1 => {
        let filter2 = arr2.filter(item2 => {
            return item1.code == item2.code && item1.context == item2.context && item1.selector == item2.selector
        })
        return filter2.length >= 1
    });
    return filter;
};

const union = (arr1, arr2) => {
    let intersection = intersect(arr1, arr2);

    let onlyInArr1 = arr1.filter(item1 => {
         let filter2 = intersection.filter(item2 => {
            return item1.code == item2.code && item1.context == item2.context && item1.selector == item2.selector
        })
        return filter2.length == 0;
    });
    return onlyInArr1.concat(arr2);
};

async function writeIOUCSV(targetPageURL, isIntersection, resultContainer, issues) {
    var result = resultContainer;
    result.issues = issues;

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

    let i = intersect(mobileResult.issues, desktopResult.issues);
    let u = union(mobileResult.issues, desktopResult.issues);
    
    let intersectionResult = Object.assign({}, mobileResult);
    let unionResult = Object.assign({}, mobileResult);

    await writeIOUCSV(url, true, intersectionResult, i);
    await writeIOUCSV(url, false, unionResult, u);

    return [url, desktopResult, mobileResult, intersectionResult, unionResult];
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
        console.log("Analysis for ", this.url);
        console.log("Number of Desktop issues : " + this.desktop.issues.length);
        console.log("Number of Mobile issues : " + this.mobile.issues.length);
        console.log("Number of intersection issues : " + this.intersection.issues.length);
        console.log("Number of union issues : " + this.union.issues.length);
        console.log("Number of issues that appear only on Desktop : " + (this.desktop.issues.length - this.intersection.issues.length));
        console.log("Number of issues that appear only on Mobile : " + (this.mobile.issues.length - this.intersection.issues.length));
        console.log("Intersection over Union : " + this.intersectionOverUnion());
    }

    intersectionOverUnion() {
        return this.intersection.issues.length / this.union.issues.length;
    }
}

// Usage
async function main() {
    targetURLs = [
        "https://nytimes.com",
        "https://usability.yale.edu/web-accessibility"
    ]
    
    analysisResults = []
    for (url of targetURLs) {
        res = await run(url);
        analysisRes = new AnalysisResult(res[0], res[1], res[2], res[3], res[4]);
        analysisResults.push(analysisRes);
    }
    for (res of analysisResults) {
        res.description();
    }  
}
main();