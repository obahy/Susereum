# Health Family Transaction
## Description.
The health family provides a methodology for managing health functions.

The health family handles the business logic to process Susereum's protocol which controls all operations related to health functions (commits and process new health).

Transactions within the health family have a common format that helps to keep a consist structure.

## Family
* family_name: "health"
* family_version: "1.0"

## Dependencies
Code Smell Family

## Format
type|id|data|state|time
----|--|----|-----|----
health|github_user|health|processed|yyyy-mm-dd-hh-mm-ss

The above table represents an example of a health transaciton. Each column is separate by a comma.
1. __**type**__: represent the type of transaction, the family could have two type of transactions health, and commit.
2. __**id**__: represent the transaction's id.
3. __**data**__: represent the payload of each transaction.
4. __**state**__: represent the state of a transaction on ay given moment, a transaction could have different state througout its cycle.
5. __**time**__: represent the moment that a transaction was created, the time attribute is only use on transactions of type proposal.

Regarding the execution and more information regarding health family refer to [Family Specification](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
