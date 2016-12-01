import pexpect
import commands

def send_command_to_cli_and_receive_text(cli_command):
    ret = commands.getstatusoutput(cli_command)
    return ret[1]