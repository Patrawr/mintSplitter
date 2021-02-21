import time

from datetime import date, datetime

class Splitter: 
    """Class that has the ability to split mint transactions in two
       
       For all accounts passed into the split_transactions method
       eligible transactions will be split into two transactions, 
       changing one of their categories to "Hide from Budgets and Trends". 

       The percentage of the split is set to 50% by default but can be changed
       on a per account basis.
    """

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

    def get_filtered_accounts(self):
        accounts = self.mint.get_accounts(True)
        print("Retrieved accounts")

        # filters out inactive accounts, and unrelated accounts
        accounts[:] = [
            account for account in accounts
            if account['isActive'] == True and account['accountType'] in ('credit', 'bank')
                ]

        return accounts


    def split_transactions(self, selected_accounts, start_date):
        for account in selected_accounts:

            #navigate to transaction page for specific account
            try: 
                self.mint.driver.get(f"https://mint.intuit.com/transaction.event?accountId={account['id']}")
                print(f"Navigating to account {account['accountName']}")
            except:
                print(f"Cannot find transactions for {account['accountName']}")


            # isChild field determines if it's joint or not, date is mm/dd/yy format
            txns = self.mint.get_transactions_json(id=account["id"], start_date=start_date)

            joint_txns=[]

            for txn in txns:
                if  not txn["isChild"] and txn["category"] not in ("Hide from Budgets & Trends", "Transfer") and \
                txn["isDebit"] and not txn["isPending"]:
                    joint_txns.append(txn)
                    self.submit_split_form(txn)

            print(f"Split {len(joint_txns)} txns for {account['accountName']}")

