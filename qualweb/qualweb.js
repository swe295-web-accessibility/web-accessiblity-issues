'use strict';

const { parse } = require('json2csv');
const { QualWeb, generateEARLReport } = require('@qualweb/core');
const fs = require('fs');


(async () => {
    const plugins = {
        // Check https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-adblocker
        adBlock: true, // Default value = false
        // Check https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth
        stealth: true // Default value = false
    };
    const qualweb = new QualWeb(plugins);

    const clusterOptions = {
        maxConcurrency: 5, // Performs several urls evaluations at the same time - the higher the number given, more resources will be used. Default value = 1
        timeout: 60 * 1000, // Timeout for loading page. Default value = 30 seconds
        monitor: true // Displays urls information on the terminal. Default value = false
    };

    const launchOptions = {
    };

    // Starts the QualWeb core engine
    await qualweb.start(clusterOptions, launchOptions);

    // QualWeb evaluation report
    const qualwebOptions = {
        "urls": ["https://www.nytimes.com"], // Array of urls
        // "file": "/csv/", // urls must be separated by a newline (\n)
        "viewport": {
            "mobile": false, // default value = false
            "landscape": true, // default value = viewPort.width > viewPort.height
            "userAgent": "custom user agent", // default value for desktop = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0', default value for mobile = 'Mozilla/5.0 (Linux; U; Android 2.2; en-us; DROID2 GLOBAL Build/S273) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
            "resolution": {
                "width": 1080, // default value for desktop = 1366, default value for mobile = 1080
                "height": 1920 // default value for desktop = 768, default value for mobile = 1920
            }
        },
        "waitUntil": ["load", "networkidle0"], // Events to wait before starting evaluation, default value = "load". For more check https://github.com/puppeteer/puppeteer/blob/v10.1.0/docs/api.md#pagegotourl-options
        "translate": "en", // OR { "translate": "en", "fallback": "en" } OR { own translation object } check https://github.com/qualweb/locale#readme. Default = "en"
        "execute": {
            // choose which modules to execute
            "wappalyzer": false, // wappalyzer module (https://github.com/qualweb/wappalyzer) - default value = false
            "act": false, // act-rules module (https://github.com/qualweb/act-rules) - default value = true
            "wcag": true, // wcag-techniques module (https://github.com/qualweb/wcag-techniques) - default value = true
            "bp": false, // best-practices module (https://github.com/qualweb/best-practices) - default value = true
            "counter": false // counter module (https://github.com/qualweb/counter) - default value = false
        },
        "wcag-techniques": {
            // More information about this options at https://github.com/qualweb/wcag-techniques
            "levels": ["AA"], // Conformance levels to execute,
            "principles": ["Perceivable", "Operable", "Understandable", "Robust"] // Principles to execute
        }
    }

    const urlToFileName = (url) => {
        return url.replaceAll("://", "-").replaceAll("/", "-").replaceAll(".", "-");
    }
    const makeCsvFile = (result) => {
        let url = qualwebOptions.urls.filter(url => {
            if (qualwebOptions.viewport.mobile) {

                let name = `${urlToFileName(url)}-mobile`
                var csvFilePath = 'csv/' + name + '.csv';
            }else{
                let name = `${urlToFileName(url)}-desktop`
                var csvFilePath = 'csv/' + name + '.csv';
            }

            const modules = result[url].modules;
            const assertions = modules['wcag-techniques']['assertions'];

            var resultList = [];
            // const failedAssertions = Object.keys(assertions).filter(key => assertions[key]?.metadata);
            const failedAssertions = Object.keys(assertions).filter(key => assertions[key]);
            console.log(failedAssertions)
            for (const failedAssertion of failedAssertions) {
                resultList.push(modules['wcag-techniques']['assertions'][failedAssertion].metadata)
                // console.log(failedAssertion, modules['wcag-techniques']['assertions'][failedAssertion].metadata)
            }

            const csvResult = parse(resultList);

            fs.writeFile(csvFilePath, csvResult, err => {
                if (err) {
                    console.error(err);
                }
            });
        })
    }

    // Evaluates the given options - will only return after all urls have finished evaluating or resulted in an error
    const reports = await qualweb.evaluate(qualwebOptions);

    // const csv = parse(reports);
    // console.log(modules);
    // console.log(csv.getJSONObject(qualwebOptions.urls[0]).getJSONObject('modules'));
    makeCsvFile(reports);


    // const csv = parse(reports);
    // console.log(csv);
 //   console.log(parseReports[qualwebOptions.urls[0]]);
    //  {
    //    "url": "report",
    //    "url2": "report2"
    //  }

    // Stops the QualWeb core engine
    await qualweb.stop();

    const earlOptions = {
        // Check the options in the section below
    };

    // if you want an EARL report
    // const earlReports = generateEARLReport(reports, earlOptions);



    // console.log(earlReports);
    //  {
    //    "url": "earlReport",
    //    "url2": "earlReport2"
    //  }
})();