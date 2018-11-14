# tests_python
Python tests for continuous integration

#to run all tests:
in test folder:
`export PYTHONPATH=.`
`nosetests`

#test suites
to use fast test suite - preferable during development
`nosetests -a fast`

for slow tests
`nosetests -a slow`

for load tests
`nosetests -a load`

