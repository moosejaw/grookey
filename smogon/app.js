/*
An app-type thing for parsing Smogon dex pages...

I need zombie.js and express to run so please install
those first.
*/
// Set up the zombie browser
//const Browser = require('zombie');

// Now the express stuff
const express = require('express');
const app     = express();

app.get('/api/', function(req, res) {
    res.send('Hi from Node!');
})

app.listen(process.env.port);