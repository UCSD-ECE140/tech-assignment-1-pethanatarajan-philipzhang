from pydantic import BaseModel
from typing import List, Tuple
import random

class State(BaseModel):
    teammateNames: List[str]
    teammatePositions: List[Tuple[int, int]]
    enemyPositions: List[Tuple[int, int]]
    currentPosition: Tuple[int, int]
    coin1: List[Tuple[int, int]]
    coin2: List[Tuple[int, int]]
    coin3: List[Tuple[int, int]]
    walls: List[Tuple[int, int]]

# Given the state, find the best move
# Param: state
# Return: 'w', 'a', 's', or 'd' depending ont he best move
def bestMove(state: State):
    out = ['a', 's', 'd', 'w']
    chosen = random.choice(out)
    return chosen