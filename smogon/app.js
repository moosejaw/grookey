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

app.get('/api/', function(req, res) {
    // Make a browser object
    //let txt = "you shouldn't see this";
    let metagame = req.query.metagame;
    let pokemon  = req.query.pkmn;
    let url = `http://www.smogon.com/dex/${metagame}/pokemon/${pokemon}`;

    // Call the URL grabber function thingy
    let browser = new Browser();
    browser.visit(url).then(() => {
        browser.pressButton('.ExportButton');
        let txt = browser.text('textarea');
        res.send(txt);
    },
    () => { res.send('404'); } // on reject
    );
})

app.listen(process.env.PORT);