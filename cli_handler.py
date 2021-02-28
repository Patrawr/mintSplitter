from PyInquirer import prompt, print_json
import json

SETTINGS_TEMPLATE = {'selectedAccounts': []}
SETTINGS_PATH = "settings.json"

def open_settings_file():
    # 1 check if file exists, if so open
    # 2 check if is empty or not, if not write template out
    settings = {}

    with open(SETTINGS_PATH, "a+") as settings_file:
        try:
            settings_file.seek(0)
            settings = json.load(settings_file)
        except ValueError:
            # write to json file if empty or corrupted
            settings_file.truncate(0)
            json.dump(SETTINGS_TEMPLATE, settings_file)
            settings_file.seek(0)
            settings = json.load(settings_file)
        except IOError:
            print("OS Level Error, ensure settings file is not in use somewhere else")

    return settings

def save_settings(settings_obj):
    with open(SETTINGS_PATH, "w") as settings_file:
        try:
            json.dump(settings_obj, settings_file)
        except IOError:
            print("Issues saving your configuration")


# extract account number with last four digits unmasked
def filter_answers(answer): 
    split_answers = answer.split('|')
    return split_answers[1].strip()


def get_account_selection_from_cli(accounts):
    accountChoices = []

    # generates account selection question
    for filteredAccount in accounts:
        accountChoices.append({'name': f"{filteredAccount['fiName']}  {filteredAccount['accountName']} | {filteredAccount['yodleeAccountNumberLast4']} | ${filteredAccount['currentBalance']}"})


    account_questions = [
        {
            'type': 'checkbox',
            'name': 'selectedAccounts',
            'message': "Select accounts to split.",
            'qmark': '💸',
            'choices': accountChoices
        }
    ]

    # prompts the user to select from retrieved accounts and saves them
    selected_accounts = prompt(account_questions)
    
    print("Saving your selections...")
    save_settings(selected_accounts)

    return selected_accounts



# handles retrieving either saved accounts from file or accounts selected by user from CLI
def get_selected_accounts(accounts):
    selected_accounts = {}
    selected_accounts_obj = []

    settings = open_settings_file()
    
    # if accounts are found previously saved in the settings file, load those
    # if not, prompt the user to select new accounts
    if settings["selectedAccounts"]:
        print(f"Would you still like to use these settings?\n\n")
        print("Currently Selected Accounts To Split")
        print("--------------------------------------")
        for account in settings["selectedAccounts"]:
            print(account)

        selected_accounts = settings
    else:
        selected_accounts = get_account_selection_from_cli(accounts)

    # get the mint accounts object for each selected account
    for answer in selected_accounts["selectedAccounts"]:
        for account in accounts:
            if account['yodleeAccountNumberLast4'] == filter_answers(answer):
                selected_accounts_obj.append(account)

    return selected_accounts_obj