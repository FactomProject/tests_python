import unittest, os, binascii, time, hashlib
import json

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address

@attr(fast=True)
class CLITestsDiagnostics(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    api_factomd = APIObjectsFactomd()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')

    TIME_TO_WAIT = 5

    def setUp(self):
        # self.ecrate = self.cli_create.get_entry_credit_rate()
        # imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'],
        #                                                       self.data['ec_wallet_address'])
        # self.first_address = imported_addresses[0]
        # self.entry_credit_address = imported_addresses[1]
        pass

    def test_diagnostics(self):
        result = self.cli_chain.get_diagnostics()
        self.assertIn('Name', result)
        self.assertIn("ID:", result)
        self.assertIn("PublicKey:", result)
        self.assertIn("Role:", result)
        self.assertIn("LeaderHeight:", result)
        self.assertIn("CurrentMinute:", result)
        self.assertIn("CurrentMinuteDuration:", result)
        self.assertIn("PrevMinuteDuration:", result)
        self.assertIn("BalanceHash:", result)
        self.assertIn("TempBalanceHash:", result)
        self.assertIn("LastBlockFromDBState:", result)
        self.assertIn("Status:", result)
        self.assertIn("Received:", result)
        self.assertIn("Expected:", result)
        self.assertIn("InProgress:", result)
        self.assertIn("VMIndex:", result)
        self.assertIn("FedIndex:", result)
        self.assertIn("FedID:", result)
        self.assertIn("Round:", result)



    def test_diagnostics_server(self):
        result = self.cli_chain.get_diagnostics_server()
        self.assertIn("Name:",result)
        self.assertIn("ID:", result)
        self.assertIn("PublicKey:", result)
        self.assertIn("Role:", result)

        new_dict = self.cli_chain.parse_diagnostics(result)
        id = self.cli_chain.get_diagnostics_server("-I")
        self.assertEqual(new_dict['ID'],id,"ID not returned correctly")

        name = self.cli_chain.get_diagnostics_server("-N")
        self.assertEqual(new_dict['Name'], name, "Name not returned correctly")

        public_key = self.cli_chain.get_diagnostics_server("-K")
        self.assertEqual(new_dict['PublicKey'], public_key, "Public Key not returned correctly")

        role = self.cli_chain.get_diagnostics_server("-R")
        self.assertEqual(new_dict['Role'], role, "Role not returned correctly")


    def test_diagnostics_network(self):
        result = self.cli_chain.get_diagnostics_network()
        self.assertIn("LeaderHeight:", result)
        self.assertIn("CurrentMinute:", result)
        self.assertIn("CurrentMinuteDuration:", result)
        self.assertIn("PrevMinuteDuration:", result)
        self.assertIn("BalanceHash:", result)
        self.assertIn("TempBalanceHash:", result)
        self.assertIn("LastBlockFromDBState:", result)

        new_dict = self.cli_chain.parse_diagnostics(result)

        leader_height = self.cli_chain.get_diagnostics_network("-L")
        self.assertEqual(new_dict['LeaderHeight'],leader_height,"Leader Height not returned correctly")

        current_minute = self.cli_chain.get_diagnostics_network("-M")
        self.assertEqual(new_dict['CurrentMinute'], current_minute, "Current Minute not returned correctly")

        #Current duration can never be same to compare, hence only verifying that it is not 0.
        current_minute_duration = self.cli_chain.get_diagnostics_network("-D")
        self.assertNotEqual(current_minute_duration,0,"current duration is 0")

        previous_minute_duration = self.cli_chain.get_diagnostics_network("-P")
        self.assertEqual(new_dict['PrevMinuteDuration'], previous_minute_duration, "Pre Minute Duration not returned correctly")

        balance_hash = self.cli_chain.get_diagnostics_network("-H")
        self.assertEqual(new_dict['BalanceHash'], balance_hash, "Balance Hash not returned correctly")

        temp_balance_hash = self.cli_chain.get_diagnostics_network("-T")
        self.assertEqual(new_dict['TempBalanceHash'], temp_balance_hash, "Temp Balance Hash not returned correctly")

        lastblock = self.cli_chain.get_diagnostics_network("-B")
        self.assertEqual(new_dict['LastBlockFromDBState'], lastblock, "LastBlockFromDBState not returned correctly")


    def test_diagnostics_sync(self):
        result = self.cli_chain.get_diagnostics_sync()
        self.assertIn("Status:", result)
        self.assertIn("Received:", result)
        self.assertIn("Expected:", result)

        new_dict = self.cli_chain.parse_diagnostics(result)
        status = self.cli_chain.get_diagnostics_sync("-S")
        self.assertEqual(new_dict['Status'],status, "Status not returned correctly")

        status = self.cli_chain.get_diagnostics_sync("-R")
        self.assertEqual(new_dict['Received'], status, "Received not returned correctly")

        status = self.cli_chain.get_diagnostics_sync("-E")
        self.assertEqual(new_dict['Expected'], status, "Expected not returned correctly")


    def test_diagnostics_authset(self):
        result = self.cli_chain.get_diagnostics_authset()
        self.assertIn("Leaders", result)
        self.assertIn("ID:", result)
        self.assertIn("VM:", result)
        self.assertIn("ProcessListHeight:", result)
        self.assertIn("ListLength:", result)
        self.assertIn("NextNil", result)
        self.assertIn("Audits", result)
        self.assertIn("Online:", result)

    def test_diagnostics_election(self):
        result = self.cli_chain.get_diagnostics_election()
        self.assertIn("InProgress:", result)
        self.assertIn("VMIndex:", result)
        self.assertIn("FedIndex:", result)
        self.assertIn("FedID:", result)
        self.assertIn("Round:", result)

        new_dict = self.cli_chain.parse_diagnostics(result)
        inprogress = self.cli_chain.get_diagnostics_election("-P")
        self.assertEqual(new_dict['InProgress'], inprogress, "Inprogress not returned correctly")

        vmindex = self.cli_chain.get_diagnostics_election("-V")
        self.assertEqual(new_dict['VMIndex'], vmindex, "VM Index not returned correctly")

        fedindex = self.cli_chain.get_diagnostics_election("-F")
        self.assertEqual(new_dict['FedIndex'], fedindex, "Fed Index not returned correctly")

        fedid = self.cli_chain.get_diagnostics_election("-I")
        self.assertEqual(new_dict['FedID'], fedid, "Fed ID not returned correctly")

        round = self.cli_chain.get_diagnostics_election("-R")
        self.assertEqual(new_dict['Round'], round, "Round not returned correctly")


    def test_currentminute(self):
        result = self.cli_chain.get_currentminute()
        print(result)
        self.assertIn("LeaderHeight:",result)
        self.assertIn("DirectoryBlockHeight:", result)
        self.assertIn("Minute:", result)
        self.assertIn("CurrentBlockStartTime:", result)
        self.assertIn("CurrentMinuteStartTime:", result)
        self.assertIn("CurrentTime:", result)
        self.assertIn("DirectoryBlockInSeconds:", result)
        self.assertIn("StallDetected:", result)
        self.assertIn("FaultTimeout:", result)
        self.assertIn("RoundTimeout:", result)

        currentminute = self.cli_chain.get_currentminute("-M")
        currentminute_diag = self.cli_chain.get_diagnostics_network("-M")
        self.assertEqual(currentminute,currentminute_diag, "Current minutes are not matching")

        leaderheight_curmin = self.cli_chain.get_currentminute(" -L ")
        leaderheight_diag = self.cli_chain.get_diagnostics_network(" -L ")

        if currentminute !=0:
            #plus one for now until FD-1241 is fixed.
            self.assertEqual(str(int(leaderheight_curmin)+1),leaderheight_diag,"Leader Height not matching")
        else:
            self.assertEqual(leaderheight_curmin, leaderheight_diag, "Leader Height not matching")

        dblock_height_curmin = int(self.cli_chain.get_currentminute("-D"))
        if currentminute ==0:
            self.assertEqual(leaderheight_curmin,str(dblock_height_curmin), "Directory Block height not matching")
        else:
            self.assertEqual(leaderheight_curmin, str(int(dblock_height_curmin)), "Directory Block height not matching")


        blockstarttime = self.cli_chain.get_currentminute("-B")
        self.assertNotEqual(blockstarttime,0,"Block Start Time is 0.")

        currminstarttime = self.cli_chain.get_currentminute("-N")
        self.assertNotEqual(currminstarttime,0,"Current Minute Start Time is 0")

        currmin = self.cli_chain.get_currentminute("-T")
        self.assertNotEqual(currmin,0,"Current Minute is 0")

        dblock_in_seconds =  self.cli_chain.get_currentminute("-S")
        self.assertNotEqual(dblock_in_seconds,0,"Directory Block in seconds is 0")

        stall_detected = self.cli_chain.get_currentminute("-X")
        self.assertNotEqual(stall_detected,"true","There is a stall in network.")

        fault_timeout = self.cli_chain.get_currentminute("-F")
        self.assertNotEqual(fault_timeout,0,"Fault timeout is 0")

        round_timeout = self.cli_chain.get_currentminute("-R")
        self.assertNotEqual(round_timeout,0,"Round timeout is 0")


    def test_admin_block(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']
        ablock_by_height = self.cli_chain.get_ablock_by_height(dbheight)
        #fetch the backreference hash since it is the keymr in the output
        keymr = ablock_by_height[19:83]
        lookuphash = ablock_by_height[96:160]
        prevbackreferencehash = ablock_by_height[184:248]


        ablock_by_keymr = self.cli_chain.get_ablock_by_keymr(keymr)
        #compare the outputs by height and keymr to verify the output returned is exact same.
        self.assertEqual(ablock_by_height,ablock_by_keymr,"ablocks are not matching")

        #test ablock with flags
        backreferencehash = self.cli_chain.get_ablock_by_height(dbheight, " -B ")
        self.assertEqual(backreferencehash,keymr,"backreferencehash not matching")

        height = self.cli_chain.get_ablock_by_height(dbheight," -D ")
        self.assertEqual(dbheight,height,"heights are matching")

        lookuphash_new = self.cli_chain.get_ablock_by_height(dbheight," -L ")
        self.assertEqual(lookuphash,lookuphash_new,"lookup hash not match")

        prevbackreferencehash_new = self.cli_chain.get_ablock_by_height(dbheight,"-P ")
        self.assertEqual(prevbackreferencehash,prevbackreferencehash_new," Previous Back Reference Hash does not natch")

        raw = self.cli_chain.get_ablock_by_height(dbheight, " -R ")
        self.assertNotEqual(raw,"","No value returned for raw")

    def test_directory_block(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']
        dblock_by_height = self.cli_chain.get_dblock_by_height(dbheight)
        self.assertIn("DBHash:",dblock_by_height,"DBHash is not available")
        self.assertIn("KeyMR:", dblock_by_height, "KeyMR is not available")
        self.assertIn("HeaderHash:", dblock_by_height, "HeaderHash is not available")
        self.assertIn("SequenceNumber:", dblock_by_height, "SequenceNumber is not available")
        self.assertIn("Version:", dblock_by_height, "Version is not available")
        self.assertIn("NetworkID:", dblock_by_height, "NetworkID is not available")
        self.assertIn("BodyMR:", dblock_by_height, "BodyMR is not available")
        self.assertIn("PrevKeyMR:", dblock_by_height, "PrevKeyMR is not available")
        self.assertIn("PrevFullHash:", dblock_by_height, "PrevFullHash is not available")
        self.assertIn("Timestamp:", dblock_by_height, "Timestamp is not available")
        self.assertIn("DBHeight:", dblock_by_height, "DBHeight is not available")
        self.assertIn("BlockCount:", dblock_by_height, "BlockCount is not available")

        keymr = dblock_dict['KeyMR']
        dblock_by_keymr = self.cli_chain.get_directory_block(keymr)
        self.assertEqual(dblock_by_height,dblock_by_keymr,"Output from dblock keymr and heights are not matching")

    def test_directory_block_by_flags(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']

        dblock_headerhash = self.cli_chain.get_dblock_by_height(dbheight, " -A ")
        self.assertEqual(dblock_dict['HeaderHash'],dblock_headerhash,"Header Hash is not matching")

        bodymerkelroot = self.cli_chain.get_dblock_by_height(dbheight, " -B ")
        self.assertEqual(dblock_dict['BodyMR'],bodymerkelroot," Body Merkel Root is not matching")

        dblockcount = self.cli_chain.get_dblock_by_height(dbheight, " -C ")
        self.assertEqual(dblock_dict['BlockCount'],dblockcount, "Block Count is not matching")

        dblockheight = self.cli_chain.get_dblock_by_height(dbheight," -D ")
        self.assertEqual(dblock_dict['DBHeight'], dblockheight, "DB height is not matching")

        prevfullhash = self.cli_chain.get_dblock_by_height(dbheight, " -F ")
        self.assertEqual(dblock_dict['PrevFullHash'], prevfullhash, "Previous Full Hash is not matching")

        dbhash = self.cli_chain.get_dblock_by_height(dbheight, " -H ")
        self.assertEqual(dblock_dict['DBHash'], dbhash, "Directory Block hash is not matching")

        keymr = self.cli_chain.get_dblock_by_height(dbheight, " -K ")
        self.assertEqual(dblock_dict['KeyMR'], keymr, "KeyMR is not matching")

        networkid = self.cli_chain.get_dblock_by_height(dbheight, " -N ")
        self.assertEqual(dblock_dict['NetworkID'], networkid, "Network ID is not matching")

        prevkeymr = self.cli_chain.get_dblock_by_height(dbheight, " -P ")
        self.assertEqual(dblock_dict['PrevKeyMR'], prevkeymr, "Previous KeyMR is not matching")

        rawdblock = self.cli_chain.get_dblock_by_height(dbheight, " -R ")
        self.assertNotEqual(rawdblock,0,"Raw directory block is empty")

        timestamp = self.cli_chain.get_dblock_by_height(dbheight, " -T ")
        self.assertEqual(dblock_dict['Timestamp'], timestamp, "Time stamp is not matching")

        version = self.cli_chain.get_dblock_by_height(dbheight, " -V ")
        self.assertEqual(dblock_dict['Version'], version, "Version is not matching")


    def test_entrycredit_block(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']
        ecblock_by_height = self.cli_chain.get_ecblock_by_height(dbheight)
        self.assertIn("HeaderHash:",ecblock_by_height, "Header hash is not available")
        self.assertIn("PrevHeaderHash:", ecblock_by_height, "Prev Header Hash is not available")
        self.assertIn("FullHash:", ecblock_by_height, "Full Hash is not available")
        self.assertIn("PrevFullHash:", ecblock_by_height, "Previous Full Hash is not available")
        self.assertIn("BodyHash:", ecblock_by_height, "Body Hash is not available")
        self.assertIn("DBHeight:", ecblock_by_height, "DB Height is not available")
        self.assertIn("Entries", ecblock_by_height, "Entries is not available")
        self.assertIn("MinuteNumber:", ecblock_by_height, "Minute Number is not available")
        self.assertIn("EntryCommit", ecblock_by_height, "Entry Commit is not available")
        self.assertIn("Version:", ecblock_by_height, "Version is not available")
        self.assertIn("Millitime:", ecblock_by_height, "Millitimestamp is not available")
        self.assertIn("EntryHash:", ecblock_by_height, "EntryHash is not available")
        self.assertIn("Credits:", ecblock_by_height, "Credits is not available")
        self.assertIn("ECPubKey:", ecblock_by_height, "EC Public Key is not available")
        self.assertIn("Signature", ecblock_by_height, "Signature is not available")

        for i in range(1,11):
            self.assertIn("MinuteNumber: " + str(i), ecblock_by_height, "Minutes from 1 to 10 is not available")

        ecblock = self.cli_chain.parse_block_data(ecblock_by_height)
        keymr = ecblock['HeaderHash']
        ecblock_by_keymr =  self.cli_chain.get_ecblock_by_keymr(keymr)
        self.assertEqual(ecblock_by_height, ecblock_by_keymr, "Output from ecblock keymr and height is not matching")


    def test_entrycredit_block_with_flags(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']
        ecblock_by_height = self.cli_chain.get_ecblock_by_height(dbheight)
        ecblock = self.cli_chain.parse_block_data(ecblock_by_height)
        headexpansionarea = self.cli_chain.get_ecblock_by_height(dbheight, " -A ")
        self.assertEqual(headexpansionarea,'[]',"Header expansion is not set to empty value")

        bodyhash = self.cli_chain.get_ecblock_by_height(dbheight, " -B ")
        self.assertEqual(ecblock['BodyHash'], bodyhash, "Body Hash is not matching")

        ec_dbheight = self.cli_chain.get_ecblock_by_height(dbheight," -D ")
        self.assertEqual(dbheight, ec_dbheight," DB Height is not matching")

        fullhash = self.cli_chain.get_ecblock_by_height(dbheight, " -F ")
        self.assertEqual(ecblock['FullHash'], fullhash, "Full Hash is not matching")

        headerhash = self.cli_chain.get_ecblock_by_height(dbheight, " -H ")
        self.assertEqual(ecblock['HeaderHash'], headerhash, "Header Hash is not matching")

        prevfullhash = self.cli_chain.get_ecblock_by_height(dbheight, " -L ")
        self.assertEqual(ecblock['PrevFullHash'], prevfullhash, "Previous Full Hash is not matching")

        prevheaderhash = self.cli_chain.get_ecblock_by_height(dbheight," -P ")
        self.assertEqual(ecblock['PrevHeaderHash'], prevheaderhash, "Previous Header Hash is not matching")

        rawecblock = self.cli_chain.get_ecblock_by_height(dbheight, " -r ")
        self.assertNotEqual(rawecblock,0,"Raw EC Block is empty")

    def test_factoid_block_with_flags(self):
        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)
        dbheight = dblock_dict['DBHeight']
        fblock_height = self.cli_chain.get_fblock_by_height(dbheight)

        # fblock = self.cli_chain.get_factoid_block_by_height(dbheight,"-r")
        #commenting this comparison as the format of the output is not same for factom-cli get fblock and factom-cli get fbheight.
        #sometime in future this needs to be fixed.
        # self.assertEqual(fblock,fblock_height,"Outputs of fblock and fblock by height are not matching")

        fblock_by_heights = self.cli_chain.parse_fblock_data(fblock_height)
        bodymr = self.cli_chain.get_fblock_by_height(dbheight, " -B ")
        self.assertEqual(fblock_by_heights['bodymr'], bodymr, "BodyMR is not matching")

        fblock_dbheight = self.cli_chain.get_fblock_by_height(dbheight, " -D ")
        self.assertEqual(dbheight, fblock_dbheight, "DB Height is not matching")

        exchrate = self.cli_chain.get_fblock_by_height(dbheight, " -E ")
        self.assertEqual(str(fblock_by_heights['exchrate']), exchrate, "Exchange Rate is not matching")

        prevledgerkeymr = self.cli_chain.get_fblock_by_height(dbheight, " -L ")
        self.assertEqual(fblock_by_heights['prevledgerkeymr'], prevledgerkeymr, "Previous Ledger Key MR is not matching")

        prevkeymr = self.cli_chain.get_fblock_by_height(dbheight, " -P ")
        self.assertEqual(fblock_by_heights['prevkeymr'], prevkeymr, "Previous Key MR is not matching")

        rawfblock = self.cli_chain.get_fblock_by_height(dbheight, " -R ")
        self.assertNotEqual(rawfblock, 0 , "Raw factoid block is empty")

    def test_get_head_with_flag(self):

        dblock = self.cli_chain.get_latest_directory_block()
        dblock_dict = self.cli_chain.parse_block_data(dblock)

        headerhash = dblock_dict['HeaderHash']
        headerhash_flag = self.cli_chain.get_latest_directory_block(flag_list=['-A'])
        self.assertEqual(headerhash, headerhash_flag, "Header Hash is not matching")

        bodymr = dblock_dict['BodyMR']
        bodymr_flag = self.cli_chain.get_latest_directory_block(flag_list=['-B'])
        self.assertEqual(bodymr, bodymr_flag, "Body MR is not matching")

        blockcount = dblock_dict['BlockCount']
        blockcount_flag =  self.cli_chain.get_latest_directory_block(flag_list=['-C'])
        self.assertEqual(blockcount, blockcount_flag, "Block Count is not matching")

        dbheight = dblock_dict['DBHeight']
        dbheight_flag = self.cli_chain.get_latest_directory_block(flag_list=['-D'])
        self.assertEqual(dbheight, dbheight_flag, "DB height is not matching")

        prevfullhash = dblock_dict['PrevFullHash']
        prevfullhash_flag = self.cli_chain.get_latest_directory_block(flag_list=['-F'])
        self.assertEqual(prevfullhash, prevfullhash_flag, "Previous Full Hash is not matching")

        dbhash = dblock_dict['DBHash']
        dbhash_flag =  self.cli_chain.get_latest_directory_block(flag_list=['-H'])
        self.assertEqual(dbhash, dbhash_flag, "DB Hash is not matching")

        keymr = dblock_dict['KeyMR']
        keymr_flag = self.cli_chain.get_latest_directory_block(flag_list=['-K'])
        self.assertEqual(keymr, keymr_flag, "Key MR is not matching")

        networkid = dblock_dict['NetworkID']
        networkid_flag = self.cli_chain.get_latest_directory_block(flag_list=['-N'])
        self.assertEqual(networkid, networkid_flag, "Network ID is not matching")

        prevkeymr = dblock_dict['PrevKeyMR']
        prevkeymr_flag = self.cli_chain.get_latest_directory_block(flag_list=['-P'])
        self.assertEqual(prevkeymr, prevkeymr_flag, "Prev Key MR is not matching")

        raw_flag =  self.cli_chain.get_latest_directory_block(flag_list=['-R'])
        self.assertNotEqual(raw_flag,0,"Raw data is empty")

        timestamp =  dblock_dict['Timestamp']
        timestamp_flag = self.cli_chain.get_latest_directory_block(flag_list=['-T'])
        self.assertEqual(timestamp, timestamp_flag, "Time stamp is not matching")

    def test_get_heights_with_flag(self):
        heights = self.cli_chain.get_heights()
        heights = self.cli_chain.parse_simple_data(heights)

        dbheight = heights['DirectoryBlockHeight']
        dbheight_with_flag =  self.cli_chain.get_heights_with_flag(" -D ")
        self.assertEqual(dbheight,dbheight_with_flag,"DB height is not matching")

        leaderheight = heights['LeaderHeight']
        leaderheight_with_flag = self.cli_chain.get_heights_with_flag( " -L ")
        self.assertEqual(leaderheight, leaderheight_with_flag, "Leader Height is not matching")

        entryblockheight = heights['EntryBlockHeight']
        entryblockheight_with_flag = self.cli_chain.get_heights_with_flag(" -B ")
        self.assertEqual(entryblockheight, entryblockheight_with_flag, "Entry Block Height is not matching")

        entryheight = heights['EntryHeight']
        entryheight_with_flag = self.cli_chain.get_heights_with_flag( " -E ")
        self.assertEqual(entryheight, entryheight_with_flag, "Entry Height is not matching")


    def test_get_tps(self):
        tps = self.cli_chain.get_tps()
        tps = self.cli_chain.parse_simple_data(tps)
        instant = self.cli_chain.get_tps(" -I ")
        instant = round(float(instant),2)
        self.assertEqual(instant,float(tps['Instant']),"Instant not matching")
        total = self.cli_chain.get_tps(" -T ")
        total = round(float(total),2)
        self.assertEqual(total, float(tps['Total']), "Total not matching")

    def test_properties(self):
        properties = self.cli_chain.get_properties()
        parsed_properties = self.cli_chain.parse_simple_data(properties)

        api_version = self.cli_chain.get_properties(" -A ")
        self.assertEqual(api_version, parsed_properties['FactomdAPIVersion'],"Factomd API version is not matching")

        cli_version = self.cli_chain.get_properties(" -C ")
        self.assertEqual(cli_version, parsed_properties['CLI Version'],"CLI version is not matching")

        factomd_version = self.cli_chain.get_properties(" -F ")
        self.assertEqual(factomd_version, parsed_properties['FactomdVersion'], "Factomd version is not matching")

        wallet_api_version = self.cli_chain.get_properties(" -L ")
        self.assertEqual(wallet_api_version, parsed_properties['WalletAPIVersion'], "Wallet API version is not matching")

        wallet_version = self.cli_chain.get_properties(" -W ")
        self.assertEqual(wallet_version, parsed_properties['WalletVersion'], "Wallet version is not matching")