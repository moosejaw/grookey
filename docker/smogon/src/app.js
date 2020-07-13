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


function getURLString(meta, pkmn) {
    return `http://www.smogon.com/dex/${meta}/pokemon/${pkmn}`
}

function getResponseTemplate(url) {
    return {
        data: {},
        url: url,
        code: 404
    }
}

function getPokemonTypeList(browser) {
    let type_list = [];
    let types = browser.queryAll('.TypeList');
    for (let item of types[0].children) {
        if (type_list.length == 2) { break; }
        else {
            type_list.push(item.textContent.toLowerCase());
        }
    }
    return type_list;
}

app.get('/movesets/', (req, res) => {
    let browser = new Browser();

    // Make a browser object
    let url = getURLString(req.query.metagame, req.query.pkmn);
    let resp = getResponseTemplate(url);

    browser.visit(url).then(
        // Fulfilled
        () => {
            // Get the typing of the pokemon
            resp.data.types = getPokemonTypeList(browser);

            // Get the moveset data
            resp.data.movesets = [];
            let movesets = browser.queryAll('.ExportButton');
            if (movesets.length > 0) {
                // Push the button and copy/paste the textarea stuff
                movesets.forEach((v, i) => {
                    browser.pressButton(v);
                    resp.data.movesets.push(
                        browser.query('textarea').textContent
                    );
                    browser.pressButton(v);
                });

                // Find the tier of the Poke
                resp.data.tier = '';
                let tierDone = false;
                browser.queryAll('tr').forEach((v, i) => {
                    if (!tierDone && v.children.item(0).textContent == 'Tier') {
                        resp.data.tier = v.children.item(1).textContent;
                        tierDone = true;
                    }
                });

                // Now do the ugly thing to get the moveset titles...
                // TODO: Don't make this check every single div on the page, there must be a better way
                resp.data.titles = [];
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

                // Push the titles into the array
                titles.forEach((v, i) => { resp.data.titles.push(v); });

                resp.code = 200;
                res.send(resp);
            }
            else {
                // No moveset data! Send a 405 error.
                resp.code = 405;
                res.send(resp);
            }
        },

        // Rejected
        () => { 
            res.send(resp); 
        }
    );
});

app.get('/formats/', (req, res) => {
    // Setup
    let browser = new Browser();
    let url = getURLString(req.query.metagame, req.query.pkmn);
    let resp = getResponseTemplate(url);

    browser.visit(url).then(
        // Fulfilled
        () => {
            let div = browser.queryAll('.PokemonPage-StrategySelector');
            if (div.length == 0) { resp.code = 405; } 
            else {
                resp.data.formats = [];
                // div with class name -> ul (children[2])-> li (children)
                for (let item of div[0].children[2].children) {
                    resp.data.formats.push(item.textContent.toLowerCase())
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

app.get('/basestats/', (req, res) => {
    // Setup
    let browser = new Browser();
    let url = getURLString(req.query.metagame, req.query.pkmn);
    let resp = getResponseTemplate(url);

    browser.visit(url).then(
        // Fulfilled
        () => {
            // Get the typing of the pokemon
            resp.data.types = getPokemonTypeList(browser);

            // Get stats
            resp.data.stats = [];
            let stat_table = browser.queryAll('.PokemonStats');
            // First set of stats -> tbody -> trs containing data
            for (let item of stat_table[0].children[0].children) {
                let txt = item.textContent.match(/^.*:[0-9]{1,3}/g);
                if (!txt.length) {
                    console.log('Non-match found (unexpected)');
                } else {
                    resp.data.stats.push(txt[0].split(':'));
                }
            }
            resp.code = 200;
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