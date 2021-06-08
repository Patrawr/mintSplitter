import splitter as mint_splitter
import mintapi
import keyring
import cli_handler as cli
import sys

KEYRING_SERVICE = 'mint_splitter'


def main():
    print('Starting splitter')

    user = keyring.get_password(KEYRING_SERVICE, "user")
    password = ''

    # if credentials already saved in keyring...
    if user:
        password = keyring.get_password(KEYRING_SERVICE, "password")
    else:
        user, password = cli.save_credentials(KEYRING_SERVICE)

    print("Logging in...")
    try:
        mint = mintapi.Mint(
            email=user,
            password=password,
            mfa_method='sms',
            headless=True,
            session_path="./session",
            wait_for_sync=False
        )
    except:
        print("Failed to login to mint/open new chrome session. Ensure your current chrome session is closed")
        exit()

    print("Logged in!")

    splitter = mint_splitter.Splitter(mint)
    accounts = splitter.get_filtered_accounts()

    selected_accounts = cli.get_selected_accounts(accounts)

    splitter.split_transactions(
        selected_accounts, start_date=cli.get_start_date())

    mint.close()

    sys.exit()


if __name__ == '__main__':
    main()
