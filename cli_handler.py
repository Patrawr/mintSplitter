from PyInquirer import prompt, print_json

def filter_answers(answer): 
    split_answers = answer.split('|')
    return split_answers[1].strip()

# presents retrieved mint accounts to user in CLI and returns list of mint account objects corresponding to selection
def get_accounts_from_user_selection(accounts):
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