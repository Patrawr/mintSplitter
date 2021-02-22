from PyInquirer import prompt, print_json
import json

SETTINGS_TEMPLATE = {'selectedAccounts': []}

def open_settings_file():
    # 1 check if file exists, if so open
    # 2 check if is empty or not, if not write template out
    settings = {}

    with open("settings.json", "a+") as settings_file:
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

def check_settings():

    settings = open_settings_file()

    print(settings)
    print()

def filter_answers(answer): 
    split_answers = answer.split('|')
    return split_answers[1].strip()

# presents retrieved mint accounts to user in CLI and returns list of mint account objects corresponding to selection
def get_accounts_from_user_selection(accounts):
    check_settings()

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
            if account['yodleeAccountNumberLast4'] == filter_answers(answer):
                selected_accounts_obj.append(account)

    return selected_accounts_obj