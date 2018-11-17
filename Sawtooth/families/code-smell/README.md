# Code Smell Family Transaction
## Description.
The code-smell family provides a methodology for managing code smell functions.

The code-smell family handles the business logic to process Susereum's protocol which controls all operations related to code smells (load default configuration, propose new metrics, and vote for proposals).

Transactions within the code-smell family have a common format that helps to keep a consist structure between them.

## Family
* family_name: "code_smell"
* family_version: "1.0"

## Dependencies
None

## Format
type|id|data|state|time
----|--|----|-----|----
code-smell|name|metric|create|yyyy-mm-dd-hh-mm-ss

The above table represents an example of a code smell transaciton. Each column is separate by a comma.
1. __**type**__: represent the type of transaction, the family could have three type of transactions code_smell, proposal, and vote.
2. __**id**__: represent the transaction's id.
3. __**data**__: represent the payload of each transaction.
4. __**state**__: represent the state of a transaction on ay given moment, a transaction could have different state througout its cycle.
5. __**time**__: represent the moment that a transaction was created, the time attribute is only use on transactions of type proposal.

Regarding the execution and more information regarding code smell family refer to [Family Specification](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
