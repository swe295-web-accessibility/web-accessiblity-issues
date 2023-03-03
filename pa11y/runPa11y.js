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

async function runPa11y(url, isMobile) {
    try {
        const replacedURL = url.replaceAll("://", "-").replaceAll(".", "-");
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
    } catch (error) {
        console.log(error);
    }
}

const targetPageURL = "https://nytimes.com";

runPa11y(targetPageURL, true);
runPa11y(targetPageURL, false);