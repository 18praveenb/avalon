#!/usr/bin/env zsh
git push heroku master && heroku ps:scale web=1
