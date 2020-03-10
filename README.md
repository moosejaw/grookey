# grookeybot
A discord bot for Pokémon related stuff. This is a hobby project.

# Installing
To install you need Docker and Docker Compose. You also need to get your bot token from the Discord dashboard and copy/paste it into a `.env` file, where the variable is named `TOKEN`.

Then all you need to do is open a terminal, navigate to this folder and run:
```
sudo docker-compose up -d
```

The containers are all built from the `docker-compose.yml` files and their respective `Dockerfile`s.

# Containers
## Bot
Based on the slim Python 3.7 image, this container runs the bot code.

## Smogon
This is a Node-based API which uses Express to route requests sent from the bot to retrieve Smogon moveset information about specific Pokémon in a specific metagame.

To get the Smogon data, Zombie is used as a headless browser. The URL is built from the commands given through Discord, and the page is 'rendered' using Zombie. Then, specific DOM queries are made to extract moveset titles, movesets, and the tier of the Pokémon. This data is returned to the bot along with a code indicating success/fail.

This kind of manipulation isn't perfect and can cause the bot to crash for specific Pokémon but it works most of the time. Even Gen I & II where abilities/held items didn't exist return okay.

If the response succeeds, the bot sends a pretty version of the response data.

# Disclaimer
I'm not affiliated with Smogon.