import os
import sys
from brownie import network, accounts

ldo_token_address = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"
dai_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
steth_token_address = "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"
steth_token_kernel = "0xb8ffc3cd6e7cf5a098a1c92f48009765b24088dc"
one_inch_token_address = "0x111111111117dc0aa78b770fa6a738034120c302"
one_inch_token_owner = "0x5E89f8d81C74E311458277EA1Be3d3247c7cd7D1"
lido_dao_agent_address = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"
lido_dao_voting_address = "0x2e59A20f205bB85a89C53f1936454680651E618e"
lp_token_address = "0xc5578194d457dcce3f272538d1ad52c68d1ce849"


gas_price = "90 gwei"
rewards_amount = 200000
scale = 10
initial_rewards_duration_sec = 60 * 60 * 24 * 30 # one month


def get_is_live():
    return network.show_active() != "development"


def get_deployer_account(is_live):
    if is_live and "DEPLOYER" not in os.environ:
        raise EnvironmentError(
            "Please set DEPLOYER env variable to the deployer account name"
        )

    return accounts.load(os.environ["DEPLOYER"]) if is_live else accounts[0]


def prompt_bool():
    choice = input().lower()
    if choice in {"yes", "y"}:
        return True
    elif choice in {"no", "n"}:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
