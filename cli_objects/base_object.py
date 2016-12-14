import os

class FactomBaseObject():
    _gopath = os.environ['GOPATH']
    _factom_cli_command = _gopath + '/src/github.com/FactomProject/factom-cli/factom-cli -w 10.32.0.9:8089 -s 10.29.0.5:8088 '
