import random
from typing import List, Tuple
from app.models.user import User


def generate_pairs(users: List[User]) -> Tuple[List[Tuple[User, User]], List[User]]:
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
