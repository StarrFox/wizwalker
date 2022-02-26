# install enviroment
install:
  poetry install

# start wiz instance and then start debug cli
cli: install
  poetry run wizwalker start-wiz
  poetry run wizwalker

# build docs
docs: install
  cd docs && poetry run make html

# publish a major, minor, or patch version
publish TYPE:
  poetry version {{TYPE}}
  poetry build
  poetry publish

