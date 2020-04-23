#!/usr/bin/env zsh
./build.zsh && ./commit.zsh $1 update && ./deploy.zsh
