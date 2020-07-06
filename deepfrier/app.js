/*
    Deep fried image generator for discord bot
    
    awaits a request a /api/ with a filename and a flag
    sends 400 if failed
    200 if OK
*/
const { exec } = require('child_process');
const express = require('express');
const app     = express();

app.post('/api/', function(req, res) {
    let filename    = req.query.filename;
    let df_filename = "df_".concat(filename);
    let intense     = req.query.intense; // do an intense deep fry

    // convert image to jpg
    var failed = false;

    exec(`magick ${process.env.DEEPFRY_DIR}/${filename} -quality 6 -modulate 105,200,100 -posterize 8 ${process.env.DEEPFRY_DIR}/${df_filename}`,
        (error, stdout, stderr) => {
            if (error !== null || stdout !== "" || stderr !== "") {
                failed = true;
            }
            console.log(`stderr: ${stderr}`);
            console.log(`stdout: ${stdout}`);
        }
    );
    if (failed) { 
        console.log('deep frying failed!'); 
        res.send({code: 400})
    } else {
        console.log('success!')
        // send success code
        res.send({code: 200, filename: df_filename})
    }
});


app.listen(process.env.PORT);