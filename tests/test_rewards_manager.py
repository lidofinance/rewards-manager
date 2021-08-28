import pytest
from brownie import reverts, ZERO_ADDRESS, chain, accounts, RewardsManager
from utils.config import lido_dao_agent_address, rewards_amount, gift_index


def test_owner_is_deployer(rewards_manager, ape):
    assert rewards_manager.owner() == ape


def test_stranger_cannot_transfer_ownership(rewards_manager, stranger):
    with reverts("not permitted"):
        rewards_manager.transfer_ownership(stranger, {"from": stranger})


def test_ownership_can_be_transferred(rewards_manager, ape, stranger):
    tx = rewards_manager.transfer_ownership(stranger, {"from": ape})

    assert rewards_manager.owner() == stranger
    assert len(tx.events) == 1
    assert tx.events[0]['new_owner'] == stranger


def test_ownership_can_be_transferred_to_zero_address(rewards_manager, ape):
    rewards_manager.transfer_ownership(ZERO_ADDRESS, {"from": ape})

    assert rewards_manager.owner() == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_cannot_set_rewards_contract(rewards_manager, stranger):
    assert rewards_manager.rewards_contract() != ZERO_ADDRESS

    with reverts("not permitted"):
        rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_can_set_rewards_contract(rewards_manager, ape):
    assert rewards_manager.rewards_contract() != ZERO_ADDRESS

    tx = rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": ape})

    assert rewards_manager.rewards_contract() == ZERO_ADDRESS
    assert len(tx.events) == 1
    assert tx.events[0]['rewards_contract'] == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_check_is_rewards_period_finished(rewards_manager, stranger):
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True


@pytest.mark.usefixtures("set_rewards_contract")
def test_period_finish(rewards_manager, farming_rewards):
    assert farming_rewards.tokenRewards(gift_index)[4] == rewards_manager.period_finish()


def test_stranger_cannot_start_next_rewards_period_without_rewards_contract_set(rewards_manager, stranger):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_cannot_start_next_rewards_period_with_zero_amount(rewards_manager, stranger):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_starts_next_rewards_period(rewards_manager, ldo_token, stranger):
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})

    assert ldo_token.balanceOf(rewards_manager) > 0
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    rewards_manager.start_next_rewards_period({"from": stranger})

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_cannot_start_next_rewards_period_while_current_is_active(rewards_manager, ldo_token, stranger):
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})
    rewards_manager.start_next_rewards_period({"from": stranger})

    chain.sleep(1)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})

    with reverts("manager: rewards period not finished"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_start_next_rewards_period_after_current_is_finished(rewards_manager, ldo_token, stranger):
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})
    rewards_manager.start_next_rewards_period({"from": stranger})

    chain.sleep(1000000)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})
    rewards_manager.start_next_rewards_period({"from": stranger})

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False


def test_stranger_cannot_recover_erc20(rewards_manager, ldo_token, stranger):
    with reverts("not permitted"):
        rewards_manager.recover_erc20(ldo_token, 0, {"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_recovers_erc20_to_own_address(rewards_manager, ldo_token, ape):
    assert ldo_token.balanceOf(rewards_manager) == 0


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_recovers_erc20_to_stranger_address(rewards_manager, ldo_token, ape, stranger):
    assert ldo_token.balanceOf(rewards_manager) == 0

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": accounts.at(lido_dao_agent_address, force=True)})
    assert ldo_token.balanceOf(rewards_manager) == rewards_amount

    rewards_manager.recover_erc20(ldo_token, rewards_amount, stranger, {"from": ape})
    assert ldo_token.balanceOf(stranger) == rewards_amount
