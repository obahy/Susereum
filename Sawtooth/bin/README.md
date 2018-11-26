# Suserum Family binaries
This section contains the main scripts of all family transactions, each component of the family (client, processor) can be execute from this directory.

All scripts require python3, scripts that end with 'tp' manage the business logic py scripts handles the client interface.

## How to run
The following example demostrate how to run the code smell family processor and how to implement a default load of the code smells.

Start code smell processor:
`python3 codesmell-tp -v`

Do a default code smell:
`python3 code_smell.py default --path $SAWTOOTH_HOME --url REST_API`

As demostrate above both components are required to process transactions, the '.py' script sends the request and the 'tp' script validate and approve the trasanction.
