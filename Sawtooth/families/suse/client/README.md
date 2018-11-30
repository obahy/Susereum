# Suse Family Transaction - Client.
## Description.
The client module is responsible for the communication between final users and internal sawtooth components,
whenever users send a transaction, the client module gets the request, parsed it and then forwards it to the
rest api. The suse client only process requests related to the suse family. The module consist of three scripts
suse_cli.py (a command line interface), suse_client.py (suse family front end) and suse_exceptions.py

## Functions
suse client has several functions that can be use to send transactions and review those transactions within the chain.

### suse
`suse(self, new_health=None, github_id=None)`<br>
Generate suse based on new projects health.<br>
ARGS: health created from commit, id of user who made the commit

### list
`list(self,type=None)`<br>
Return a list of transactions, the type defines which kind of transaction will be returned.<br>
ARGS: type (type of transaction to list)

More Information regarding the suse family, can be found at [Suse Family](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
