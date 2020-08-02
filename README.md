# WizWalker
Wizard101 bot for autoquesting

## install
download latest release from [here](https://github.com/StarrFox/WizWalker/releases)

## discord
join the offical discord [here]()

## development install
This package uses [poetry](https://python-poetry.org/)
```shell script
$ poetry install --dev
```

## running
Shell must have admin perms
```shell script
$ poetry shell
$ py -m wizwalker
```

## building
```shell script
$ pyinstaller -F --uac-admin wizwalker/__main__.py
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
