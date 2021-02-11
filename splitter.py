import mintapi
import keyring
import time
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# takes in a monetary amount, strips off the $ and splits into two equal floats,
# with 2 decimal precision
def calculate_split(total_amount):
    splits = []
    stripped_amount = float(total_amount.replace('$', ''))

    splits.append(round(stripped_amount / 2, 2))
    splits.append(round(stripped_amount - splits[0], 2))
    return splits


def submit_split_form(mint, txn):
    url = 'https://mint.intuit.com/updateTransaction.xevent'

    split_amounts = calculate_split(txn['amount'])

    data = {'task': 'split',
            'data': '', 
            'txnId': f"{txn['id']}:0",
            'token': mint.token,
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
            'categoryId1': 40
            }

    result = mint.post(url, data=data)

    print(f"Split {txn['merchant']} for {txn['amount']} on {txn['date']}")

# start of script #############################################################################################
print ('Starting splitter')
username = keyring.get_password("mint_splitter", "user")
pw = keyring.get_password("mint_splitter", "password")

print("Logging in...")
mint = mintapi.Mint(
    username,
    pw,
    mfa_method='sms',
    headless=False,
    mfa_input_callback=None,
    session_path="./session",
    wait_for_sync=False
)

print("Logged in!")

accounts = mint.get_accounts(True)
print("Retrieved accounts")

joint_card = accounts[34]

#navigate to transaction page for specific account
try: 
    mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={joint_card['id']}")
    print(f"Navigating to account {joint_card['accountName']}")
except:
    print(f"Cannot find transactions for {joint_card['accountName']}")


# isChild field determines if it's joint or not, date is mm/dd/yy format
txns = mint.get_transactions_json(id=joint_card["id"], start_date="12/24/20")
print(f"Retrieved {len(txns)} txns for {joint_card['accountName']}")


joint_txns=[]

for txn in txns:
    if  not txn["isChild"] and txn["category"] != "Hide from Budgets & Trends" and txn["isDebit"] and not txn["isPending"]:
        joint_txns.append(txn)
        submit_split_form(mint, txn)