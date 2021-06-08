# mintsplitter

A python script built on top of mrooney's wonderful mintapi project, that logs into mint and automatically splits transactions in half from select accounts for you. The resulting transaction will have half it's amount split off and categorized as Hidden from budgets & Trends.

## Use Case
If you share a joint account with someone but are frustrated that transactions from said joint accounts do not accurately represent your own spending (i.e., you contribute to half of each transaction). This will split and hide a portion of the transaction (default 50%) leaving you with accurate budgets and trends.

#

## Installation
Ensure you have python 3 and pip and then :

 ```TBD``

## Dependencies
If running module directly via cmdline, ensure you have the following packages installed:
- [keyring](https://github.com/jaraco/keyring)
- [mintapi](https://github.com/mrooney/mintapi)
- [PyInquirer](https://github.com/CITGuru/PyInquirer)
