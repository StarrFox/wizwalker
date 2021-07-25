# WizWalker

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Wizard101 scripting library

## documentation
you can find the documentation [here](https://starrfox.github.io/wizwalker/)

## install
```shell
$ pip install -U wizwalker
```

## discord
join the offical discord [here](https://discord.gg/JHrdCNK)

## development install
This package uses [poetry](https://python-poetry.org/)
```shell
$ poetry install
```

## running
Shell may need admin perms
```shell
$ poetry shell
$ wizwalker
```

## building
You'll need the dev install (see above) for this to work

### exe
```shell
# Admin if needed
$ pyinstaller -F --uac-admin --name WizWalker wizwalker/__main__.py
# Normal
$ pyinstaller -F --name WizWalker wizwalker/__main__.py
```

### wheel and source
```shell
$ poetry build
```

### Docs
```shell
$ cd docs
$ make html
```

## console commands
wizwalker: Runs the wizwalker cli

wizwalker start-wiz: start wizard101 instances

wizwalker wad: edit and extract wizard101 wad files
