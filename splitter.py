import mintapi
import keyring
import time

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
        sample_txn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"transaction-{transaction_id}"))
        )
    except:
        print('Cannot find transaction element')
    else:    
        sample_txn.click()

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

# start of script #############################################################################################
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

#navigate to transaction page for specific account
try: 
    mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={joint_card['id']}")
except:
    print('Cannot find transactions for account: $$$$')

time.sleep(3)

locate_and_split_txn(mint.driver, "1368494644", 25.82)
locate_and_split_txn(mint.driver, "1369145342", 45.61)

# isChild field determines if it's joint or not
txns = mint.get_transactions_json(id=joint_card["id"], start_date="1 December 2020")


joint_txns=[]

for txn in txns:
    if txn["isChild"]:
        joint_txns.append(txn)
        print (txn)


print (joint_txns)