import pexpect

def send_command_to_cli_and_receive_text(cli_command):
    p = pexpect.spawn(cli_command)
    p.expect(pexpect.EOF)
    return p.before