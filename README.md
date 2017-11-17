# tests_python
[![CircleCI](https://circleci.com/gh/FactomProject/tests_python.svg?style=shield&circle-token=80f863fcd9484403e6d7b30c8b8952ff3361bc27)]
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

