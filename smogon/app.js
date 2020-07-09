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


app.get('/movesets/', (req, res) => {
    console.log(`Started responding to a req at ${getTimeInSecs()}`);

    let browser = new Browser();
    console.log(`Opened a new browser instance at ${getTimeInSecs()}`);

    // Make a browser object
    let url = `http://www.smogon.com/dex/${req.query.metagame}/pokemon/${req.query.pkmn}`;
    let resp = {
        data: [],
        titles: [],
        tier: '',
        url: url,
        types: [],
        code: 404
    };

    // Go to the smogon page
    console.log(`Going to visit ${url}`);
    browser.visit(url).then(
        () => {
            console.log(`Visited ${url}`);
            console.log(`Loaded the page at ${getTimeInSecs()}`);

            // Get the typing of the pokemon
            let types = browser.queryAll('.TypeList');
            for (let item of types[0].children) {
                if (resp.types.length == 2) { break; }
                else {
                    resp.types.push(item.textContent.toLowerCase());
                }
            }

            // Get the moveset data
            let movesets = browser.queryAll('.ExportButton');
            if (movesets.length > 0) {
                // Push the button and copy/paste the textarea stuff
                movesets.forEach((v, i) => {
                    browser.pressButton(v);
                    resp.data.push(browser.query('textarea').textContent);
                    browser.pressButton(v);
                });

                console.log(`Got the moveset data at ${getTimeInSecs()}`);

                // Find the tier of the Poke
                let tierDone = false;
                browser.queryAll('tr').forEach((v, i) => {
                    if (!tierDone && v.children.item(0).textContent == 'Tier') {
                        console.log(`Found a tier at index ${i} of trs. The tier is ${v.children.item(1).textContent}`);
                        resp.tier = v.children.item(1).textContent;
                        tierDone = true;
                        console.log('Set the tierDone to true');
                    }
                });

                // Now do the ugly thing to get the moveset titles...
                // TODO: Don't make this check every single div on the page, there must be a better way
                let titles = new Set();
                browser.queryAll('div').forEach((v, i) => {
                    let btns  = v.getElementsByClassName('ExportButton');
                    if (btns.length > 0) {
                        let title = v.getElementsByTagName('h1').item(0).textContent;

                        // This is probably kind of bad?
                        if (title.toLowerCase() != req.query.pkmn && title.toLowerCase() != 'overview') {
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
                // No moveset data! Send a 405 error.
                resp.code = 405;
                res.send(resp);
            }
        },
        () => { 
            console.log(`Rejected promise (404) at ${getTimeInSecs()}`);
            console.log(`Returning ${JSON.stringify(resp)}`);
            res.send(resp); 
        }
    );
});

app.get('/formats/', (req, res) => {
    // Setup
    let browser = new Browser();
    let url = `http://www.smogon.com/dex/${req.query.metagame}/pokemon/${req.query.pkmn}`;
    let resp = {
        data: [],
        url: url,
        code: 404
    };

    browser.visit(url).then(
        // Fulfilled
        () => {
            let div = browser.queryAll('.PokemonPage-StrategySelector');
            if (div.length == 0) { resp.code = 405; } 
            else {
                // div with class name -> ul (children[2])-> li (children)
                for (let item of div[0].children[2].children) {
                    resp.data.push(item.textContent.toLowerCase())
                }
                resp.code = 200;
            }
            res.send(resp);
            
        },
        // Rejected
        () => {
            resp.code = 404;
            res.send(resp);
        }
    );
});

app.listen(process.env.PORT);