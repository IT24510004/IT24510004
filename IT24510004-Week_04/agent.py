# agent.py
from collections import deque
import heapq
import random
import math

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
    """An agent that uses classical search algorithms (BFS, DFS, UCS) to find paths to food."""

    def __init__(self, search_type='BFS'):
        self.active_algo = search_type  # Lab 03 - Step 1.3
        self.plan = []                  # Lab 03 - Step 1.3

    def get_successors(self, state, grid_size, walls):
        """Returns a list of valid (next_state, action, cost) tuples from the current state."""
        x, y = state
        width, height = grid_size
        successors = []
        
        # Define possible movements and their corresponding action names
        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        for action, (nx, ny) in moves:
            # Check grid boundaries
            if 0 <= nx < width and 0 <= ny < height:
                # Check if the target cell is not a wall
                if (nx, ny) not in walls:
                    # Cost is 1 per step
                    successors.append(((nx, ny), action, 1))

        return successors

    def bfs_search(self, start, goal_positions, grid_size, walls):
        """Breadth-First Search using a FIFO queue (deque)."""
        # Frontier stores tuples of: (current_state, path_of_actions)
        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current_state, actions = frontier.popleft()

            if current_state in goal_positions:
                return actions

            for next_state, action, cost in self.get_successors(current_state, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, actions + [action]))

        return []

    def dfs_search(self, start, goal_positions, grid_size, walls):
        """Depth-First Search using a LIFO stack (Python list)."""
        # Frontier stores tuples of: (current_state, path_of_actions)
        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current_state, actions = frontier.pop()

            if current_state in goal_positions:
                return actions

            for next_state, action, cost in self.get_successors(current_state, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, actions + [action]))

        return []

    def ucs_search(self, start, goal_positions, grid_size, walls):
        """Uniform-Cost Search using a Priority Queue (heapq) ordered by total path cost g(n)."""
        # Frontier stores tuples of: (total_cost, current_state, path_of_actions)
        frontier = [(0, start, [])]
        reached = {}  # Maps state to its best known cost

        while frontier:
            cost, current_state, actions = heapq.heappop(frontier)

            if current_state in goal_positions:
                return actions

            if current_state in reached and reached[current_state] < cost:
                continue

            reached[current_state] = cost

            for next_state, action, step_cost in self.get_successors(current_state, grid_size, walls):
                new_cost = cost + step_cost
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next_state, actions + [action]))

        return []

    # Lab 04 - Step 1.2: Implement A* Search with heuristic selection
    def astar_search(self, start, goal_positions, grid_size, walls, heuristic_type='manhattan'):
        """A* Search using a Priority Queue (heapq) ordered by f(n) = g(n) + h(n)."""
        
        # Helper function to select the correct heuristic calculation
        def calculate_heuristic(pos, goal):
            if heuristic_type.lower() == 'euclidean':
                return self.euclidean_distance(pos, goal)
            else:
                return self.manhattan_distance(pos, goal)

        # Assuming single goal for simplicity (or picking the first from goal_positions)
        goal = list(goal_positions)[0] if isinstance(goal_positions, set) else goal_positions

        # Initialize g_cost for the start node
        g_cost = 0
        h_cost = calculate_heuristic(start, goal)
        f_cost = g_cost + h_cost

        # Frontier stores tuples of: (f_cost, g_cost, current_state, path_of_actions)
        frontier = [(f_cost, g_cost, start, [])]
        reached_states = set()

        while frontier:
            # Pop the node with the lowest f_cost
            f, g, current_state, actions = heapq.heappop(frontier)

            # Check if we have reached the goal
            if current_state in goal_positions:
                return actions

            # Skip if already expanded/reached with a better cost
            if current_state in reached_states:
                continue

            reached_states.add(current_state)

            # Node expansion: check adjacent cells via get_successors
            for next_state, action, step_cost in self.get_successors(current_state, grid_size, walls):
                if next_state not in reached_states:
                    g_new = g + step_cost
                    h_new = calculate_heuristic(next_state, goal)
                    f_new = g_new + h_new

                    # Push the new tuple to the priority queue
                    heapq.heappush(frontier, (f_new, g_new, next_state, actions + [action]))

        return []

    def sense_and_act(self, percept: dict) -> str:
        """Forms a complete plan if empty, then executes it step-by-step."""
        start = tuple(percept['agent_pos'])
        grid_size = percept['grid_size']
        walls = set(percept['walls'])
        all_food = percept['all_food']

        # Check if the plan is empty and there is food available
        if not self.plan and all_food:
            
            # Find the closest food pellet using Manhattan distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1]))
            goal_set = {closest_food}  # Pass it as a set/collection to match our search methods

            algo = self.active_algo.upper()
            
            # Execute the search method matching self.active_algo
            if algo == 'BFS':
                self.plan = self.bfs_search(start, goal_set, grid_size, walls)
            elif algo == 'DFS':
                self.plan = self.dfs_search(start, goal_set, grid_size, walls)
            elif algo == 'UCS':
                self.plan = self.ucs_search(start, goal_set, grid_size, walls)
            elif algo in ['ASTAR', 'A*']: # Lab 04 - Step 1.3: Implement A* Search
                self.plan = self.astar_search(start, goal_set, grid_size, walls, heuristic_type='manhattan')
        # Return the first action from self.plan
        if self.plan:
            return self.plan.pop(0)
        
        return 'Stay'

    # Lab 04 - Step 1.1: Implement Manhattan distance heuristic
    def manhattan_distance(self, pos, goal):
        """Calculates the Manhattan distance h(n) = |x_1 - x_2| + |y_1 - y_2|."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # Lab 04 - Step 1.1: Implement Euclidean distance heuristic
    def euclidean_distance(self, pos, goal):
        """Calculates the straight-line Euclidean distance h(n) = sqrt((x_1 - x_2)^2 + (y_1 - y_2)^2)."""
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

# Lab 04 - Step 1.1: Testing Checkpoint for Heuristics
if __name__ == "__main__":
    agent = SearchAgent()
    
    start = (0, 0)
    goal = (3, 4)
    
    mh_dist = agent.manhattan_distance(start, goal)
    eu_dist = agent.euclidean_distance(start, goal)
    
    print(f"Manhattan Distance: {mh_dist}") 
    print(f"Euclidean Distance: {eu_dist}") 