# Health Family Transaction - Client.
## Description.
The client module is responsible for the communication between final users and internal sawtooth components,
whenever users send a transaction, the client module gets the request, parsed it and then forwards it to the
rest api. The health client only process requests related to the health families. The module consist of three scripts
health_cli.py (a command line interface), health_client.py (health family front end), health_exceptions.py, and health_process.py (script to calculate project health)

## Functions
health client has several functions that can be use to send transactions and review.

### commit
`commit(self, commit_url, github_user)`
Store commit into chain, forwards url to code analysis.<br>
ARGS: commit_url, github_user

### code_analysis
`code_analysis(elf, commit_url, github_user)`
call code analysis module.<br>
ARGS: commit_url, github_user

### list
`list(self, type=None, limit=None)`
Return a list of transactions, the type defines which kind of transaction will be returned.<br>
ARGS: type (type of transaction to list), limit (number of transactions to return)

More Information regarding the health family, can be found at [Health Family](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
