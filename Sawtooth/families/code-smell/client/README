# Code Smell Family Transaction - Client.
## Description.
The client module is responsible for the communication between final users and internal sawtooth components,
whenever users send a transaction, the client module gets the request, parsed it and then forwards it to the
rest api. The code smell client only process requests related to the code smell families. The module consist of three scripts
code_smell_cli.py (a command line interface), code_smell_client.py (code smell family front end) and code_smell_exceptions.py

## Functions
code-smell client has several functions that can be use to send transactions and review those transactions within the chain.

### load_default
`default(self, wait=None)`
Load default code smell configuration.<br>
ARGS: None

### propose
`propose(self, code_smells):`
Propose a new code smell metrics.<br>
ARGS: list of code smells.

### vote
`vote(self, proposal_id, vote)`
Vote for a proposal. (1=yes , 0=no)<br>
ARGS: proposal id, vote value

### list
`list(self,type=None)`
Return a list of transactions, the type defines which kind of transaction will be returned.<br>
ARGS: type (type of transaction to list)

### show
`show(self, address)`
Return a specific transaction.<br>
ARGS: transaction address.

### update code smells configurations
'_update_suse_file(self, proposal_id, state)'
The function updates the code smell configuration file with the latest accepted proposal.
if the proposal is not accepted the action is recorded in the chain. <br>
ARG: proposal id, proposal status

### _check_votes
`_check_votes(self, proposal_id, flag=None)`
Return number of votes, checking votes can be use to review the current votes or to run a proposal validation.<br>
ARGS: proposal id, flag <optional>

More Information regarding the code smell family, can be found at [Code Smell Family](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
