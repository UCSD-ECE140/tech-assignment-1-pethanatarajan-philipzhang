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
# Return: 'w', 'a', 's', or 'd' depending on the best move
def bestMove(state: State):
    # find nearest coin
    # find nearest path
    # move

    all_coins  = []
    all_coins = all_coins + state["coin1"]
    all_coins = all_coins + state["coin2"]
    all_coins = all_coins + state["coin3"]
    paths = []
    for coin in all_coins:
        grid = []
        for i in range(10):
            grid.append([-1]*10)
        grid[coin[0]][coin[1]] = 0
        for w in state["walls"]:
            grid[w[0]][w[1]] = -2
        p = bfs((state["currentPosition"][0], state["currentPosition"][1]), coin, grid)
        if p:
            paths.append(p)

    if len(paths) == 0:
        out = ['a', 's', 'd', 'w']
        chosen = random.choice(out)
        return chosen
    
    nearest_path = sorted(paths, key=lambda x: x[0])
    return nearest_path[0][1]


def bfs (start, end, grid):
    queue = [(end)]
    while len(queue) != 0:
        curr = queue.pop(0)
        #right
        if curr[1]+1 < 10 and grid[curr[0]][curr[1]+1] == -1:
            grid[curr[0]][curr[1]+1] = grid[curr[0]][curr[1]] + 1
            queue.append((curr[0],curr[1]+1))
            
        #bottom
        if curr[0]+1 < 10 and grid[curr[0]+1][curr[1]] == -1:
            grid[curr[0]+1][curr[1]] = grid[curr[0]][curr[1]] + 1
            queue.append((curr[0]+1,curr[1]))
        #left
        if curr[1]-1 >= 0 and grid[curr[0]][curr[1]-1] == -1:
            grid[curr[0]][curr[1]-1] = grid[curr[0]][curr[1]] + 1
            queue.append((curr[0],curr[1]-1))
        #top
        if curr[0]-1 >= 0 and grid[curr[0]-1][curr[1]] == -1:
            grid[curr[0]-1][curr[1]] = grid[curr[0]][curr[1]] + 1
            queue.append((curr[0]-1,curr[1]))
        
    dist = grid[start[0]][start[1]]
    # for g in grid:
    #     print(g)

    # right
    out = []
    if start[1]+1 < 10 and grid[start[0]][start[1]+1] > 0:
        out.append((grid[start[0]][start[1]+1], 'd'))
    # bottom
    if start[0]+1 < 10 and grid[start[0]+1][start[1]] > 0:
        out.append((grid[start[0]+1][start[1]], 's'))
    # left
    if start[1]-1 >=0 and grid[start[0]][start[1]-1] > 0:
        out.append((grid[start[0]][start[1]-1], 'a'))
    # top
    if start[0]-1 >= 0 and grid[start[0]-1][start[1]] > 0:
        out.append((grid[start[0]-1][start[1]], 'w'))
    
    if len(out) == 0:
        return None

    sorted_out = sorted(out, key=lambda x: x[0])

    # print((dist, sorted_out[0][1]))
    return (dist, sorted_out[0][1])

    



state = {'teammateNames': [], 'teammatePositions': [], 'enemyPositions': [], 'currentPosition': [5,5], 'coin1': [(0,0)], 'coin2': [], 'coin3': [], 'walls': [(1,0),(1,1), (1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8)]}
print(bestMove(state))