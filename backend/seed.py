"""Populate the database with a sample group so the app isn't empty on first run.

Usage: python seed.py
"""

from app import create_app
from app.extensions import db
from app.models import Expense, ExpenseSplit, Group, GroupMember, User

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    alice = User(name="Alice", email="alice@example.com")
    alice.set_password("password123")
    bob = User(name="Bob", email="bob@example.com")
    bob.set_password("password123")
    carol = User(name="Carol", email="carol@example.com")
    carol.set_password("password123")

    db.session.add_all([alice, bob, carol])
    db.session.commit()

    trip = Group(name="Goa Trip", created_by=alice.id)
    db.session.add(trip)
    db.session.commit()

    for user in (alice, bob, carol):
        db.session.add(GroupMember(group_id=trip.id, user_id=user.id))
    db.session.commit()

    hotel = Expense(group_id=trip.id, paid_by=alice.id, amount=3000, description="Hotel")
    db.session.add(hotel)
    db.session.commit()

    share = round(3000 / 3, 2)
    for user in (alice, bob, carol):
        db.session.add(ExpenseSplit(expense_id=hotel.id, user_id=user.id, amount_owed=share))

    cabs = Expense(group_id=trip.id, paid_by=bob.id, amount=600, description="Cabs")
    db.session.add(cabs)
    db.session.commit()

    cab_share = round(600 / 3, 2)
    for user in (alice, bob, carol):
        db.session.add(ExpenseSplit(expense_id=cabs.id, user_id=user.id, amount_owed=cab_share))

    db.session.commit()

    print("Seed data created.")
    print("Users: alice@example.com / bob@example.com / carol@example.com, password: password123")
    print(f"Group: '{trip.name}' (id={trip.id})")
