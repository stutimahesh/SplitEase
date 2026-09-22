import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.balances import _minimize_transactions  # noqa: E402


def test_simple_two_person_settlement():
    balances = {1: 100.0, 2: -100.0}
    result = _minimize_transactions(balances)
    assert result == [{"from": 2, "to": 1, "amount": 100.0}]


def test_three_person_settlement_minimizes_transactions():
    # Alice paid 300 for a hotel, split equally among 3 (100 each).
    balances = {"alice": 200.0, "bob": -100.0, "carol": -100.0}
    result = _minimize_transactions(balances)

    assert len(result) == 2
    assert sum(t["amount"] for t in result) == 200.0
    assert all(t["to"] == "alice" for t in result)


def test_already_settled_group_has_no_transactions():
    balances = {1: 0.0, 2: 0.0, 3: 0.0}
    assert _minimize_transactions(balances) == []


def test_settlement_result_zeroes_out_every_balance():
    balances = {"a": 50.0, "b": 30.0, "c": -20.0, "d": -60.0}
    transactions = _minimize_transactions(balances)

    net = dict.fromkeys(balances, 0.0)
    for t in transactions:
        net[t["from"]] -= t["amount"]
        net[t["to"]] += t["amount"]

    for user, starting_balance in balances.items():
        assert round(net[user], 2) == round(starting_balance, 2)
