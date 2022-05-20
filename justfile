set shell := ["powershell.exe", "-c"]

# install enviroment
install:
  poetry install

# start wiz instance and then start debug cli
cli: install
  poetry run wizwalker start-wiz
  poetry run wizwalker

# build docs
docs: install
  poetry run pdoc -t pdoc_template ./wizwalker/

# publish a major, minor, or patch version
publish TYPE: install
  poetry version {{TYPE}}
  poetry build
  poetry publish

