from heapq import heappush, heappop

class PQueue:
    def __init__(self):
        self.backing = []
        self.items = 0
    def push(self, item):
        heappush(self.backing, item)
        self.items += 1
    def pop(self):
        self.items -= 1
        return heappop(self.backing)
    def add(self, item):
        self.push(item)
    def len(self):
        return self.items

NORTH, EAST, SOUTH, WEST = range(4)
directions = {NORTH : (-1, 0), EAST : (0, 1), SOUTH : (1, 0), WEST : (0, -1)}
grid = [[9, 9, 9], [1, 9, 9], [1, 1, 1]]
# grid = [[1,4,3,2,1], [6,4,4, 2, 1], [6,3,2,1,9]]
def getNeighbor(grid, r, c, direction):
    dr, dc = directions[direction]
    return ((dr + r) % 3, (dc + c) % 3)

def invertDirection(direction):
    if direction == NORTH:
        return SOUTH
    elif direction == SOUTH:
        return NORTH
    elif direction == EAST:
        return WEST
    else:
        return EAST

def getPath(path, start, end, grid):
    actions = []
    while end != start:
        d = invertDirection(path[end])
        actions.append(d)
        end = getNeighbor(grid, end[0], end[1], d)
    return actions[::-1]



def dijkstra(grid, start, end):
    queue = PQueue()
    queue.add((0, start, None))
    visited = set()
    path = {}
    path[start] = None
    while queue.len() > 0:
        dist, current, action = queue.pop()
        if current not in visited:
            path[current] = action
            visited.add(current)
            if current == end:
                return dist, path
            n = [(getNeighbor(grid, current[0], current[1], d), d) for d in directions.keys()]
            
            # ns = [(dist + grid[r][c], (r, c), d) for  in n]
            ns = [(dist + grid[state[0]][state[1]], (state), act) for state, act in n]
            [queue.add(n) for n in ns if n[1] not in visited]


