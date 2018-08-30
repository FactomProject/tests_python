# tests_python
[![CircleCI](https://circleci.com/gh/FactomProject/tests_python.svg?style=shield&circle-token=80f863fcd9484403e6d7b30c8b8952ff3361bc27)]
Python tests for continuous integration

#before all test runs
`export PYTHONPATH=.`

#to run all tests:
in test folder:
`nosetests`

#test suits
to quickly run full regression tests
`nosetests -a fast`

to run test suite which checks balances, blocks, chains, entries between servers
`nosetests -a last`

to run checks on the production network
`nosetests -a production

to run tests which put a load on the network
`nosetests -a load`

to run tests which verify the proper operation of the faulting and election process
`nosetests -a election

