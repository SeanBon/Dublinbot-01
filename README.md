# Api.ai - sample webhook implementation in Python

This is a really simple webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# What does the service do?
Its a Dublin City information service. This is used in conjunction with API.ai to create a bit that can lookup information about a variety of subjects. 

current features included are:
*Check the weather
*Check DublinBus next bus times (by stop number)
*Tell a Chuck Norris Joke
*Search Wikipedia for an article
*Show music charts for a country
*Lookup a song title for the artist that sings it.

#Functions

# Python Version
*Python version 3.6