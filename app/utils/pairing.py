import random
from typing import List, Tuple
from app.models.user import User


def generate_pairs_for_city(users: List[User]) -> Tuple[List[Tuple[User, User]], List[User]]:
    random.shuffle(users)

    pairs = []
    remaining = []

    for i in range(len(users)):
        giver = users[i]
        receiver = users[(i + 1) % len(users)]
        if giver.id == receiver.id:
            remaining.append(giver)
        else:
            pairs.append((giver, receiver))

    return pairs, remaining


def generate_pairs_for_all_cities(city_users: dict) -> dict:
    city_pairs = {}

    for city, users in city_users.items():
        if len(users) < 2:
            city_pairs[city] = {"pairs": [], "remaining": users}
        else:
            pairs, remaining = generate_pairs_for_city(users)
            city_pairs[city] = {"pairs": pairs, "remaining": remaining}

    return city_pairs
