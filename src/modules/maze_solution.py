# coding=utf-8
MAZES = {
    (0, 0, 0, 3): {
        'horiz_walls': [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ],
        'vert_walls': [
            [0, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 0, 1, 0, 1]
        ]
    },
    (0, 1, 5, 2): {
        'horiz_walls': [
            [0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0]
        ],
        'vert_walls': [
            [0, 0, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 0, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0]
        ]},
    (0, 4, 2, 1): {
        'horiz_walls': [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 0, 0, 1]
        ],
        'vert_walls': [
            [1, 0, 0, 0, 0],
            [1, 1, 0, 1, 1],
            [0, 0, 1, 0, 1],
            [1, 1, 0, 1, 0],
            [1, 1, 1, 0, 1],
            [0, 1, 0, 1, 0]
        ]
    },
    (1, 0, 1, 5): {
        'horiz_walls': [
            [0, 0, 1, 0, 0],
            [1, 0, 1, 0, 1],
            [1, 1, 0, 0, 1],
            [0, 1, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 0, 1, 0, 0]
        ],
        'vert_walls': [
            [0, 0, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [1, 1, 0, 0, 1],
            [0, 0, 0, 0, 0]
        ]
    },
    (1, 3, 4, 1): {
        'horiz_walls': [
            [1, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0]
        ],
        'vert_walls': [
            [0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0]
        ]
    },
    (2, 3, 3, 0): {
        'horiz_walls': [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 1, 1, 0, 1],
            [0, 1, 1, 1, 1],
            [0, 1, 0, 1, 1],
            [0, 0, 0, 1, 1]
        ],
        'vert_walls': [
            [1, 0, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
    },
    (2, 4, 4, 0): {
        'horiz_walls': [
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1],
            [0, 0, 1, 0, 0]
        ],
        'vert_walls': [
            [1, 0, 1, 0, 0],
            [1, 1, 1, 0, 1],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0]
        ]
    },
    (3, 3, 5, 3): {
        'horiz_walls': [
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ],
        'vert_walls': [
            [0, 0, 1, 1, 0],
            [1, 1, 1, 0, 1],
            [0, 1, 1, 0, 1],
            [1, 1, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [0, 0, 0, 1, 0]
        ]
    },
    (3, 5, 4, 2): {
        'horiz_walls': [
            [1, 0, 0, 0, 0],
            [1, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 1],
            [0, 1, 0, 0, 0]
        ],
        'vert_walls': [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 0, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0]
        ]
    }
}

UP = '↑'
RIGHT = '→'
DOWN = '↓'
LEFT = '←'

DIRECTIONS = (
    (UP, (0, -1), True),
    (RIGHT, (1, 0), False),
    (DOWN, (0, 1), True),
    (LEFT, (-1, 0), False),
)


def no_wall_exists(start, end, other_dimen, walls):
    if end < start:
        start, end = end, start

    return walls[other_dimen][start] == 0


def valid_neighbors(current_location, maze):
    neighbors = []
    curr_x, curr_y = current_location

    for move, (delta_x, delta_y), use_y in DIRECTIONS:
        new_x, new_y = (curr_x + delta_x, curr_y + delta_y)
        if use_y:
            curr_changed, new_changed = curr_y, new_y
            other_dimen = curr_x
            walls = maze['horiz_walls']
        else:
            curr_changed, new_changed = curr_x, new_x
            other_dimen = curr_y
            walls = maze['vert_walls']

        if 0 <= new_changed < 6 and no_wall_exists(curr_changed, new_changed, other_dimen, walls):
            neighbors.append(((new_x, new_y), move))

    return neighbors


def dfs(current_location, visited, moves, target_location, maze):
    """Returns list of moves if the target is reached, or None otherwise"""
    if current_location == target_location:
        return moves

    if current_location in visited:
        return None
    visited.add(current_location)

    # Iterate through unvisited neighbors
    for neighbor, move in valid_neighbors(current_location, maze):
        moves.append(move)
        successful_moves = dfs(neighbor, visited, moves, target_location, maze)
        if successful_moves is not None:
            return successful_moves
        moves.pop()
    return None


def solve_maze(lookup_key, start_coordinates, end_coordinates):
    maze = MAZES[lookup_key]
    moves = dfs(start_coordinates, set(), [], end_coordinates, maze)
    assert moves is not None, "Could not find solution for maze!"
    return moves
