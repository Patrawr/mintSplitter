import splitter as mint_splitter
import mintapi
import keyring
import cli_handler as cli


def main():
    print('Starting splitter')

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

    selected_accounts = cli.get_selected_accounts(accounts)

    splitter.split_transactions (selected_accounts, start_date=cli.get_start_date())

    mint.close()

if __name__ == '__main__':
        main()