# In development
# WizWalker

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Wizard101 bot for autoquesting

## install
download latest release from [here](https://github.com/StarrFox/WizWalker/releases)

## discord
join the offical discord [here](https://discord.gg/JHrdCNK)

## development install
This package uses [poetry](https://python-poetry.org/)
```shell script
$ poetry install
```

## running
Shell may need admin perms
```shell script
$ poetry shell
$ py -m wizwalker
```

## building
You'll need the dev install (see above) for this to work
```shell script
# Admin if needed
$ pyinstaller -F --uac-admin --name WizWalker wizwalker/__main__.py
# Normal
$ pyinstaller -F --name WizWalker wizwalker/__main__.py
```

## console commands
wizwalker: Runs the wizwalker bot

wiz: Starts a Wizard101 instance

## project goals in order of importance
0. basic info by memory
1. able to determine current quest
2. teleportion mode
3. info by memory
4. info by packet
5. able to combat
6. cli for end users
7. gui for end users
