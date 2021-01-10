import mintapi
import keyring
import time

from selenium import webdriver


print ('hello')
username = keyring.get_password("mint_splitter", "user")
pw = keyring.get_password("mint_splitter", "password")

mint = mintapi.Mint(
    username,
    pw,
    mfa_method='sms',
    headless=False,
    mfa_input_callback=None,
    session_path="./session",
    wait_for_sync=False
)


accounts = mint.get_accounts(True)
joint_card = accounts[34]

#find and click transactions for card 
try: 
    mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={joint_card['id']}")
except:
    print('Cannot find transaction element')

time.sleep(1)




txns = mint.get_transactions_json(id=joint_card["id"], start_date="1 December 2020")
# isChild field determines if it's joint or not


joint_txns=[]

for txn in txns:
    if txn["isChild"]:
        joint_txns.append(txn)
        print (txn)


print (joint_txns)