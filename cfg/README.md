# .env file

This folder contains a sample .env file which you can modify to get the up and running quickly.

## Instructions

1. Get your token from the Discord developer dashboard, and copy/paste it into the first line. It should look like this:

```bash
TOKEN=123456789abcdefghijklmnop
```

2. Rename the file from `sample.env` to just `.env` and move it to the root folder of this repo.

## Running tests

If you want to use TravisCI to run automated tests, you'll have to adjust the environment variables in the `.travis.yml` file to match the values in your .env file. Remember to [encrypt your token!](https://docs.travis-ci.com/user/environment-variables/#encrypting-environment-variables)
