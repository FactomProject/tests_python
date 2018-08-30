import unittest, re

import subprocess

from nose.plugins.attrib import attr


@attr(election=True)
class goTestsElections(unittest.TestCase):

# NOTE: factomd MUST NOT be running when these are run
# factomd --debuglog=badMsgs --faulttimeout=10 --roundtimeout=5 for 60 second blocks runs much quicker

    def test_unittestbatch(self):
        unittestlist = filter(None, [re.findall(r'Test[^ ][^( ]*', line) for line in
    open('/home/factom/go/src/github.com/FactomProject/factomd/engine/factomd_test.go')])
        print(unittestlist)
        for unittestname in unittestlist:
            print
            print('***************************************************')
            print(unittestname)
            process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run " + str(unittestname), stdout=subprocess.PIPE, shell=True)
            print process.communicate()[0].strip()

    def test_set_up_network(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestSetupANetwork", stdout=subprocess.PIPE, shell=True)

    def test_make_leader(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestMakeALeader", stdout=subprocess.PIPE, shell=True)

    def test_election(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestAnElection", stdout=subprocess.PIPE, shell=True)

    def test_load(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestLoad", stdout=subprocess.PIPE, shell=True)

    def test_multiple_2_election(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestMultiple2Election", stdout=subprocess.PIPE, shell=True)

    def test_multiple_3_election(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestMultiple3Election", stdout=subprocess.PIPE, shell=True)

    def test_multiple_7_election(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestMultiple7Election", stdout=subprocess.PIPE, shell=True)
        print process.communicate()[0].strip()

    def test_DBsig_election_every_2nd_block(self):
        global process
        process = subprocess.Popen("cd /home/factom/go/src/github.com/FactomProject/factomd/engine/; /usr/local/go/bin/go test -run TestDBsigElectionEvery2Block", stdout=subprocess.PIPE, shell=True)
        print process.communicate()[0].strip()

    # def tearDown(self):
    #     print process.communicate()[0].strip()

