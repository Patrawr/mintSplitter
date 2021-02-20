import mintapi
import keyring
import time

from datetime import date, datetime

from selenium import webdriver
from PyInquirer import prompt, print_json

class Splitter: 
    MINT_URL = 'https://mint.intuit.com'
    UPDATE_TXN_PATH = '/updateTransaction.xevent'
    HIDE_CATEGORY = 40

    def __init__(self, mint):
        self.mint = mint

    # takes in a monetary amount, strips off the $ and splits into two equal floats,
    # with 2 decimal precision
    def calculate_split(self, total_amount):
        splits = []
        stripped_amount = float(total_amount.replace('$', ''))

        splits.append(round(stripped_amount / 2, 2))
        splits.append(round(stripped_amount - splits[0], 2))
        return splits


    def submit_split_form(self, txn):
        url = f"{self.MINT_URL}{self.UPDATE_TXN_PATH}"

        split_amounts = self.calculate_split(txn['amount'])

        data = {'task': 'split',
                'data': '', 
                'txnId': f"{txn['id']}:0",
                'token': self.mint.token,
                'amount0': split_amounts[0],
                'category0': txn['category'],
                'merchant0': txn['merchant'],
                'txnId0': 0,
                'percentAmount0': split_amounts[0],
                'categoryId0': txn['categoryId'],
                'amount1': split_amounts[1],
                'category1': 'Hide from Budgets & Trends',
                'merchant1': txn['merchant'],
                'txnId1': 0,
                'percentAmount1': split_amounts[1],
                # category for hide from budgets and trends
                'categoryId1': self.HIDE_CATEGORY
                }

        result = self.mint.post(url, data=data)

        print(f"Split {txn['merchant']} for {txn['amount']} on {txn['date']}")


    def filter_answers(self, answer): 
        split_answers = answer.split('|')
        return split_answers[1].strip()

    def get_filtered_accounts(self):
        accounts = self.mint.get_accounts(True)
        print("Retrieved accounts")

        # filters out inactive accounts, and unrelated accounts
        accounts[:] = [
            account for account in accounts
            if account['isActive'] == True and account['accountType'] in ('credit', 'bank')
                ]

        return accounts

    # presents retrieved mint accounts to user in CLI and returns list of mint account objects corresponding to selection
    def get_accounts_from_user_selection(self, accounts):
        filteredAccountChoices = []

        # generates account selection question
        for filteredAccount in accounts:
            filteredAccountChoices.append({'name': f"{filteredAccount['fiName']}  {filteredAccount['accountName']} | {filteredAccount['yodleeAccountNumberLast4']} | ${filteredAccount['currentBalance']}"})


        filtered_account_questions = [
            {
                'type': 'checkbox',
                'name': 'accounts',
                'message': "Select accounts to split.",
                'qmark': '💸',
                'choices': filteredAccountChoices
            }
        ]

        # prompts the user to select from retrieved accounts
        selected_accounts = prompt(filtered_account_questions)
        selected_accounts_obj = []

        # get the mint accounts object for each selected account
        for answer in selected_accounts["accounts"]:
            for account in accounts:
                if account['yodleeAccountNumberLast4'] == self.filter_answers(answer):
                    selected_accounts_obj.append(account)

        return selected_accounts_obj

    def split_transactions(self, selected_accounts):
        for account in selected_accounts:

            #navigate to transaction page for specific account
            try: 
                self.mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={account['id']}")
                print(f"Navigating to account {account['accountName']}")
            except:
                print(f"Cannot find transactions for {account['accountName']}")


            # isChild field determines if it's joint or not, date is mm/dd/yy format
            txns = self.mint.get_transactions_json(id=account["id"], start_date="12/05/20")


            joint_txns=[]

            for txn in txns:
                if  not txn["isChild"] and txn["category"] not in ("Hide from Budgets & Trends", "Transfer") and \
                txn["isDebit"] and not txn["isPending"]:
                    joint_txns.append(txn)
                    self.submit_split_form(txn)

            print(f"Split {len(joint_txns)} txns for {account['accountName']}")

# start of script #############################################################################################
print ('Starting splitter')

print("Logging in...")
try: 
    mint = mintapi.Mint(
        email=keyring.get_password("mint_splitter", "user"),
        password=keyring.get_password("mint_splitter", "password"),
        mfa_method='sms',
        headless=True,
        mfa_input_callback=None,
        session_path="./session",
        wait_for_sync=False
    )
except:
    print("Failed to login to mint/open new chrome session. Ensure your current chrome session is closed")
    mint.close()
    exit()

print("Logged in!")

splitter = Splitter(mint)

accounts = splitter.get_filtered_accounts()

selected_accounts = splitter.get_accounts_from_user_selection(accounts)

splitter.split_transactions (selected_accounts)

