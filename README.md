# tests_python
Python tests for continuous integration

#before all test runs
`export PYTHONPATH=.`

#to run all tests:
in test folder:
`nosetests`

#test suits
to use fast test suite - preferable durring development
`nosetests -a fast`

for slow tests
`nostests -a slow`

for load tests
`nosetests -a load`

