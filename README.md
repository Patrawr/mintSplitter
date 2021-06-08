# mintSplitter

A python script built on top of mrooney's wonderful mintapi project, that logs into mint and automatically splits transactions in half from select accounts for you. The resulting transaction will have half it's amount split off and categorized as Hidden from budgets & Trends.

## Use Case
If you share a joint account with someone but are frustrated that transactions from said joint accounts do not accurately represent your own spending (i.e., you contribute to half of each transaction). This will split and hide a portion of the transaction (default 50%) leaving you with accurate budgets and trends.

#

## Installation
Ensure you have python3 and mintapi (see below for link to install) installed on your machine. Then, clone this repo to your computer. Only running via commandline is supported currently. PyPi distribution coming soon!



## Dependencies
If running module directly via cmdline, ensure you have the following packages installed:
- [keyring](https://github.com/jaraco/keyring)
- [mintapi](https://github.com/mrooney/mintapi)
- [PyInquirer](https://github.com/CITGuru/PyInquirer)

## Usage
Run the main.py module in the src folder to start, for example:

```python3 src/main.py```

If this is your first time running mintSplitter you will need to provide your Mint credetials to login. These are only stored in your operating system's credential vault (Keychain for macOs, Windows Credential Locker etc.) and not anywhere in mintSplitter. You may be prompted by your OS to grant mintSplitter access to store these credentials. This will be required to retrieve them upon subsequent runs.

Additionally, if you have 2FA setup on mint, you will be sent a code either via email/SMS and mintSplitter will prompt you on the commandline to enter this code. Your session will be saved and this should not be required for future logins, barring any changes from Mint requiring reauthorization. 

#

mintSplitter will initially ask you to select which accounts you would like to split txns on. You can select from a list of active accounts classified as either bank/credit by mint (typically and chequing/savings or credit account). Once you make these selections, your settings will be saved for future runs. These settings can also be changed every run (mintSplitter will ask you).

By default, mintSplitter will split every transaction in all accounts you selected for the past 60 days that meet the following criteria:

- are not pending (posted)
- are not transfers or already marked as Hidden
- are debits
- are not split already

By split, it is meant that: 
- each transaction will be split into two child transactions with the amounts split evenly between them (50/50)
- one of the transactions will be set to "Hide From Budgets & Trends"

and voila! You now have more accurate budgeting and trend information for accounts shared with anyone else, or accounts where you want mint to only consider a portion of the transaction as spent by you.


## Future Features
- upload to PyPi for distribution
- customizeable split percentages
- per account settings
- split more than twice
- other updates to txns (tagging, changing categories etc.)
