// Set up zombie
const Browser = require('zombie');

// Then express...
const express = require('express');
const app     = express();

var szn_limit = 10; // Pics must not be from a season greater than this number

app.get('/api/', (req, res) => {
    let url = 'https://frinkiac.com/';

    let any_szn      = req.query.anyszn; // Override season limit?
    let caption      = req.query.caption; // Show the caption in the pic?
    let specific_szn = req.query.specific; // Get a pic from a specific season?

    // Prepare response
    let resp = {link: '', szn: 0}

    Browser.visit(url).then(
        () => {
            // Validate the pic is from a season we want
            let valid_pic = false;
            while (!valid_pic) {
                // Push the random button
                let rand_btn = Browser.query('.random').firstChild.innerText;
                Browser.pressButton(rand_btn);
                let szn = 0;

                // Use regex to find the season no.
                const szn_regex = RegExp('/Season (\d|\d\d) \//g');
                Browser.queryAll('p').forEach((v, i) => {
                    let szn_found = false;
                    if (v.innerText.test(szn_regex)) {
                        szn = parseInt(v.split('Season ')[1].split(' /')[0]);
                        szn_found = true;
                    }
                    if (szn_found) {
                        break;
                    }
                });

                // Check the season. keep going if we don't want it
                if (szn && szn <= szn_limit) {
                    valid_pic = true;
                }
            }

            // Now get the picture
            let img_link = '';
            Browser.queryAll('img').forEach((v, i) => {
                const logo_lnk = RegExp('/\.svg/g');
                if (!logo_lnk.test(v.src)) {
                    img_link = v.src;
                }
            });

            // Build the response
            resp.link = img_link;
            resp.szn  = szn;
            res.send(resp);
        }
    );
});

app.listen(process.env.PORT);