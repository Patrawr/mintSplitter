import splitter as mint_splitter
import mintapi
import keyring
import cli_handler as cli


def main():
    print('Starting splitter')

    cli.check_settings()

    print("Logging in...")
    try: 
        mint = mintapi.Mint(
            email=keyring.get_password("mint_splitter", "user"),
            password=keyring.get_password("mint_splitter", "password"),
            mfa_method='sms',
            headless=True,
            session_path="./session",
            wait_for_sync=False
        )
    except:
        print("Failed to login to mint/open new chrome session. Ensure your current chrome session is closed")
        mint.close()
        exit()

    print("Logged in!")

    splitter = mint_splitter.Splitter(mint)
    accounts = splitter.get_filtered_accounts()

    selected_accounts = cli.get_accounts_from_user_selection(accounts)

    splitter.split_transactions (selected_accounts, start_date='12/05/20')

    mint.close()

if __name__ == '__main__':
        main()