# Susereum Transaction Families
Suserum consist of three [families](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications) each of these families handles specific logic and tasks.
* __code-smell family__: process all transactions related to code smell metrics and proposals.
* __health family__: process all transactions related to github commits, and code updates submitted by developers.
* __suse family__: process the assigment and creation of suses.

### Families Format
type|id|data|state|time
----|--|----|-----|----
code-smell|LargeClass|500|create|yyyy-mm-dd-HH-MM-SS

The above table represents an example of a code smell transaciton. Each column is separate by a comma.
* __**type**__: represent the type of transaction.
* __**id**__: represent the transaction's id.
* __**data**__: represent the payload of each transaction.
* __**state**__: represent the state of a transaction on ay given moment, a transaction could have different states througout its cycle.
* __**time**__: represent the moment that a transaction was created.

![alt text](https://github.com/obahy/Susereum/wiki/images/family_encoding.PNG "Family Encoding")

### Families Components
All three families consist of two modules:
* __client__: family interface, users can interact with the family througout the client.
* __processor__: family business logic, the processor manages and validates all transactions of its family.

More Information regarding these families could be found at [Suserum Wiki](https://github.com/obahy/Susereum/wiki/Susereum-Transaction-Family-Specifications)
