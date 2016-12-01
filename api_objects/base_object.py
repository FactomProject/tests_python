import os

class FactomBaseObject():
    _gopath = os.environ['GOPATH']
    _factom_cli_command = _gopath + '/bin/factom-cli '