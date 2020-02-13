/*
An app-type thing for parsing Smogon dex pages...

I need zombie.js and express to run so please install
those first.
*/
// Set up the zombie browser
const Browser = require('zombie');

// Now the express stuff
const express = require('express');
const app     = express();

function getTimeInSecs() {
    let d = new Date();
    return d.toTimeString();
}

// Create the browser object
//var browser = new Browser();

app.get('/api/', function(req, res) {
    console.log(`Started responding to a req at ${getTimeInSecs()}`);

    let browser = new Browser();
    console.log(`Opened a new browser instance at ${getTimeInSecs()}`);

    // Make a browser object
    let metagame = req.query.metagame;
    let pokemon  = req.query.pkmn;
    let url = `http://www.smogon.com/dex/${metagame}/pokemon/${pokemon}`;
    let resp = {msgs: [], titles: [], code: 404};

    // Go to the smogon page
    browser.visit(url).then(
        () => {
            console.log(`Visited ${url}`);
            console.log(`Loaded the page at ${getTimeInSecs()}`);

            // Get the moveset data
            let movesets = browser.queryAll('.ExportButton');
            if (movesets.length > 0) {
                // Push the button and copy/paste the textarea stuff
                movesets.forEach((v, i) => {
                    browser.pressButton(v);
                    resp.msgs.push(browser.text('textarea'));
                    browser.pressButton(v);
                });

                console.log(`Got the moveset data at ${getTimeInSecs()}`);

                // Now do the ugly thing to get the moveset titles...
                // TODO: Don't make this check all divs on the page, there must be a better way
                let titles = new Set();
                browser.queryAll('div').forEach((v, i) => {
                    let btns  = v.getElementsByClassName('ExportButton');
                    if (btns.length > 0) {
                        let title = v.getElementsByTagName('h1').item(0).textContent;

                        // ughhhhhh
                        if (title.toLowerCase() != pokemon.toLowerCase() && title.toLowerCase() != 'overview') {
                            titles.add(title);
                        }
                    }
                });

                console.log(`Done iterating through the divs at ${getTimeInSecs()}`);

                // Push the titles into the array
                titles.forEach((v, i) => { resp.titles.push(v); });

                // Send the response
                console.log(`Returning the request at ${getTimeInSecs()}`);

                resp.code = 200;
                res.send(resp);
            }
            else {
                // No moveset data!
                resp.code = 405;
                res.send(resp);
            }
        },
        () => { 
            console.log(`Rejected promise (404) at ${getTimeInSecs()}`);
            res.send(resp); 
        }
    );
});

app.listen(process.env.PORT);