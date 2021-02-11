import mintapi
import keyring
import time
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def calculate_split(total_amount):
    splits = []

    splits.append(round(total_amount / 2, 2))
    splits.append(round(total_amount - splits[0], 2))
    return splits


def locate_and_split_txn(driver, transaction_id, total_amount):
    time.sleep(1)
    #find a specific transaction in list on transactions page and click on it
    try: 
        txn_row = WebDriverWait(driver, timeout=10).until(
            EC.element_to_be_clickable((By.ID, f"transaction-{transaction_id}"))
        )
    except:
        print('Cannot find transaction list element')
    else:    
        print('Found txn row to click')
        driver.execute_script("arguments[0].scrollIntoView();", txn_row)
        driver.execute_script("arguments[0].click();", txn_row)
        # txn_row.click()

    time.sleep(0.5)
    # once transaction is selected, click on toggle to bring up txn edit modal
    txn_edit_toggle = driver.find_element_by_id("txnEdit-toggle")

    txn_edit_toggle.click()

    time.sleep(0.5)
    # click on the split button in the txn edit modal once the modal is loaded
    try: 
        txn_split_bttn = driver.find_element_by_id("txnEdit-split")
        WebDriverWait(driver, 10).until(
                lambda d : "expense hide" not in d.find_element_by_id("txnEdit-form").get_attribute('class')
            )
    except:
        print('Cannot find split button element')
    else:
        txn_split_bttn.click()

    # within the split your transaction pop-up, this is how the two editable category and amount fields are returned
    split_txn_table_categories = driver.find_elements_by_xpath(
                "//*[@id='pop-split-main-table']/tbody/tr[not(@class='hide')]/td[@class='category-cell']/input[@name='category']")

    time.sleep(0.3)
    split_txn_table_categories[0].send_keys(Keys.COMMAND + "a") 
    split_txn_table_categories[0].send_keys(Keys.DELETE)
    split_txn_table_categories[0].send_keys("Hide from Budgets & Trends")

    #get input elements for amount fields in transaction pop-up
    split_txn_table_amounts = driver.find_elements_by_xpath(
                "//*[@id='pop-split-main-table']/tbody/tr[not(@class='hide')]/td[@class='amount-cell']/span/input")

    # figure out what the actual two even split amounts will be
    split_amounts = calculate_split(total_amount)

    split_txn_table_amounts[0].send_keys(Keys.COMMAND + "a")
    split_txn_table_amounts[0].send_keys(Keys.DELETE)
    split_txn_table_amounts[0].send_keys(f"{split_amounts[0]}")

    split_txn_table_amounts[1].send_keys(Keys.COMMAND + "a")
    split_txn_table_amounts[1].send_keys(Keys.DELETE)
    split_txn_table_amounts[1].send_keys(f"{split_amounts[1]}")

    split_submit_button = driver.find_element_by_id("pop-split-submit")
    split_submit_button.click()

def submit_split_form(mint, txn_id):
    url = 'https://mint.intuit.com/updateTransaction.xevent'
    data = {'task': 'split',
            'data': '', 
            'txnId': f"{txn_id}:0", 
            'token': mint.token,
            'amount0': 79.39,
            'category0': 'Groceries',
            'merchant0': 'Farm Boy',
            'txnId0': 0,
            'percentAmount0': 79.39,
            'categoryId0': 701,
            'amount1': 100,
            'category1': 'Hide from Budgets & Trends',
            'merchant1': 'Farm Boy',
            'txnId1': 0,
            'percentAmount1': 100,
            'categoryId1': 40
            }

    headers = {'accept': '*/*',
               'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'origin': 'https://mint.intuit.com',
               'referer': 'https://mint.intuit.com/transaction.event',
               'dnt': '1'
               }

    result = mint.post(url, data=data)

    print(result.text)

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
txns = mint.get_transactions_json(id=joint_card["id"], start_date="01/01/21")
print(f"Retrieved {len(txns)} txns for {joint_card['accountName']}")

submit_split_form(mint, "1376006654")

joint_txns=[]

for txn in txns:
    if  not txn["isChild"] and txn["category"] != "Hide from Budgets & Trends" and txn["isDebit"] and not txn["isPending"]:
        joint_txns.append(txn)
        time.sleep(1)
        locate_and_split_txn(mint.driver, str(txn["id"]), float(txn["amount"].replace('$', '')))
        
# convert amount from string in $9.99 format to float
# locate_and_split_txn(mint.driver, str(joint_txns[0]["id"]), float(joint_txns[0]["amount"].replace('$', '')))
# locate_and_split_txn(mint.driver, "1368494644", 25.82)
# locate_and_split_txn(mint.driver, "1369145342", 45.61)