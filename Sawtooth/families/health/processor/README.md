# Health Family Transaction - Processor
## Description.
The processor module is the back-end of all families in sawtooth, this modules handles the business logic that each
transaction must follow in order to be added to the chain. The processor module validates the data (payload) of all
transactions, if the information is correct and the data in the transaction is valid the state of that specific transaction
is store in the chain.
The family process can save information to the chain and also it can retrieve information from it.

This component consist of several modules:
* main.py, responsible for creating a processor handler that process and manage transactions.
* handler.py, responsible for validation and management of transactions.
* health_state.py, saves the final state into the chain.
* health_payload.py, verifies the correct format and structure of the payload.

More information regarding susereum components can be found at [Suserum Architecture](https://github.com/obahy/Susereum/wiki/Susereum-Architecture)
