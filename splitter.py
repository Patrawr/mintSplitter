import mintapi
import keyring
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


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


#find a specific transaction in list on transactions page and click on it
sample_txn = mint.driver.find_element_by_id("transaction-1368494644")
time.sleep(1)
sample_txn.click()

# once transaction is selected, click on toggle to bring up txn edit modal
txn_edit_toggle = mint.driver.find_element_by_id("txnEdit-toggle")
time.sleep(1)
txn_edit_toggle.click()

# click on the split button in the txn edit modal
txn_split_bttn = mint.driver.find_element_by_id("txnEdit-split")
time.sleep(1)
txn_split_bttn.click()

# within the split your transaction pop-up, this is how the two editable category and amount fields are returned
split_txn_table_categories = mint.driver.find_elements_by_xpath(
            "//*[@id='pop-split-main-table']/tbody/tr[not(@class='hide')]/td[@class='category-cell']/input[@name='category']")

split_txn_table_categories[0].clear()

split_txn_table_categories[0].send_keys(Keys.COMMAND + "a") 
split_txn_table_categories[0].send_keys(Keys.DELETE)
split_txn_table_categories[0].send_keys("Hide from Budgets & Trends")

#get input elements for amount fields in transaction pop-up
split_txn_table_amounts = mint.driver.find_elements_by_xpath(
            "//*[@id='pop-split-main-table']/tbody/tr[not(@class='hide')]/td[@class='amount-cell']/span/input")

split_txn_table_amounts[0].send_keys(Keys.COMMAND + "a")
split_txn_table_amounts[0].send_keys(Keys.DELETE)
split_txn_table_amounts[0].send_keys("12.00")

split_txn_table_amounts[1].send_keys(Keys.COMMAND + "a")
split_txn_table_amounts[1].send_keys(Keys.DELETE)
split_txn_table_amounts[1].send_keys("13.82")

split_submit_button = mint.driver.find_element_by_id("pop-split-submit")
split_submit_button.click()

txns = mint.get_transactions_json(id=joint_card["id"], start_date="1 December 2020")
# isChild field determines if it's joint or not



joint_txns=[]

for txn in txns:
    if txn["isChild"]:
        joint_txns.append(txn)
        print (txn)


print (joint_txns)