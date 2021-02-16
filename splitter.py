import mintapi
import keyring
import time

from datetime import date, datetime

from selenium import webdriver
from PyInquirer import prompt, print_json

MINT_URL = 'https://mint.intuit.com'
UPDATE_TXN_PATH = '/updateTransaction.xevent'
HIDE_CATEGORY = 40


# takes in a monetary amount, strips off the $ and splits into two equal floats,
# with 2 decimal precision
def calculate_split(total_amount):
    splits = []
    stripped_amount = float(total_amount.replace('$', ''))

    splits.append(round(stripped_amount / 2, 2))
    splits.append(round(stripped_amount - splits[0], 2))
    return splits


def submit_split_form(mint, txn):
    url = f"{MINT_URL}{UPDATE_TXN_PATH}"

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
            'categoryId1': HIDE_CATEGORY
            }

    result = mint.post(url, data=data)

    print(f"Split {txn['merchant']} for {txn['amount']} on {txn['date']}")


def filter_answers(answer): 
    split_answers = answer.split('|')
    return split_answers[1].strip()

# start of script #############################################################################################
print ('Starting splitter')

print("Logging in...")
try: 
    mint = mintapi.Mint(
        email=keyring.get_password("mint_splitter", "user"),
        password=keyring.get_password("mint_splitter", "password"),
        mfa_method='sms',
        headless=False,
        mfa_input_callback=None,
        session_path="./session",
        wait_for_sync=False
    )
except:
    print("Failed to login to mint/open new chrome session. Ensure your current chrome session is closed")

print("Logged in!")


accounts = mint.get_accounts(True)
print("Retrieved accounts")

# filters out inactive accounts, and unrelated accounts
accounts[:] = [
     account for account in accounts
     if account['isActive'] == True and account['accountType'] in ('credit', 'bank')
        ]


filteredAccountChoices = []

# generates account selection question
for filteredAccount in accounts:
    filteredAccountChoices.append({'name': f"{filteredAccount['fiName']}  {filteredAccount['accountName']} | {filteredAccount['yodleeAccountNumberLast4']} | ${filteredAccount['currentBalance']}"})


filtered_account_questions = [
    {
        'type': 'checkbox',
        'name': 'accounts',
        'message': "Select accounts to split?",
        'qmark': '💸',
        'choices': filteredAccountChoices
    }
]

selected_accounts = prompt(filtered_account_questions)
selected_accounts_obj = []

for answer in selected_accounts["accounts"]:
    for account in accounts:
        if account['yodleeAccountNumberLast4'] == filter_answers(answer):
            selected_accounts_obj.append(account)


for account in selected_accounts_obj:

    #navigate to transaction page for specific account
    try: 
        mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={account['id']}")
        print(f"Navigating to account {account['accountName']}")
    except:
        print(f"Cannot find transactions for {account['accountName']}")


    # isChild field determines if it's joint or not, date is mm/dd/yy format
    txns = mint.get_transactions_json(id=account["id"], start_date="12/05/20")


    joint_txns=[]

    for txn in txns:
        if  not txn["isChild"] and txn["category"] not in ("Hide from Budgets & Trends", "Transfer") and \
        txn["isDebit"] and not txn["isPending"]:
            joint_txns.append(txn)
            submit_split_form(mint, txn)

    print(f"Retrieved {len(joint_txns)} txns for {account['accountName']}")

