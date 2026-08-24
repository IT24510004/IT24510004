# agent.py

from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SearchAgent:

    def bfs_search(self, start,goal,get_neighbors):
        """Breadth-First Search using a FIFO queue"""
        queue = deque([(start, [])])
        reached = {start}

        while queue:
            state, path = queue.popleft()

            if state == goal:
                return path
                