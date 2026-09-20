# agent.py

from collections import deque
import heapq
import math
# import random
from logic_engine import KnowledgeBase

# Lab 01,Lab 02 - OLD AGENT
# Lab 01 - Greedy Grid Agent
# Lab 02 - SIMPLE REFLEX AGENT
# LAB 02 - MODEL-BASED AGENT

# Lab 03 - SEARCH AGENT
# The SearchAgent uses:
#     1. Breadth-First Search (BFS)
#     2. Depth-First Search (DFS)
#     3. Uniform-Cost Search (UCS)
# The agent receives:
#     - Current agent position
#     - Grid size
#     - Wall positions
#     - Food positions
# The agent then:
#     1. Selects a food target.
#     2. Searches for a path.
#     3. Stores the path as a plan.
#     4. Executes one action at a time.

# Lab 03 - Step 1.2.1 - SEARCH AGENT
class SearchAgent:

    # Lab 03 - Step 1.2.3 - Select search algorithms: BFS, DFS, or UCS
    def __init__(self, algorithm="BFS"):
        self.active_algo = algorithm.upper()
        self.plan = []

        # Lab 05 -Step 3.1 - Instantiate Knowledge Base and define safety rules
        self.kb = KnowledgeBase()
        # Rule 1: TargetVisible AND HasDust -> SafeToEngage
        self.kb.tell_rule(["TargetVisible", "HasDust"], "SafeToEngage")
        # Rule 2: SafeToEngage AND BloodseekerMissing -> Retreat
        self.kb.tell_rule(["SafeToEngage", "BloodseekerMissing"], "Retreat")

    # Lab 04 - Step 1.1.3 - MANHATTAN DISTANCE HEURISTIC
    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions.
        Formula: h(n) = |x1 - x2| + |y1 - y2|
        This is appropriate for a grid where the agent can move only Up, Down, Left, and Right."""

        x1, y1 = pos
        x2, y2 = goal
        distance = abs(x1 - x2) + abs(y1 - y2)
        return int(distance)

    # Lab 04 - Step 1.1.4 - EUCLIDEAN DISTANCE HEURISTIC
    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions.
        Formula: h(n) = sqrt((x1-x2)^2 + (y1-y2)^2)
        This represents the straight-line distance between the current position and the goal."""

        x1, y1 = pos
        x2, y2 = goal
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    # Lab 03 - Generate valid neighboring states
    def get_neighbors(self, position, walls, grid_size):
        """Return all valid neighboring states.
        Each result has the form:(new_position, action)"""

        x, y = position
        width, height = grid_size
        moves = [
            ((0, 1), "Up"),
            ((1, 0), "Right"),
            ((0, -1), "Down"),
            ((-1, 0), "Left")]
        neighbors = []

        for (dx, dy), action in moves:
            new_x = x + dx
            new_y = y + dy
            new_position = (new_x, new_y)
            inside_grid = (0 <= new_x < width and 0 <= new_y < height)
            not_wall = new_position not in walls
            if inside_grid and not_wall:
                neighbors.append((new_position, action))
        return neighbors

    # LaB 03 - Step 1.2.3 - BREADTH-FIRST SEARCH
    def bfs_search(self, start, goal, walls, grid_size):
        """BFS uses a FIFO queue.
        Because every movement has the same cost,BFS finds a shortest path in terms of 
        number of movements."""

        start = tuple(start)
        goal = tuple(goal)
        walls = {
            tuple(wall)
            for wall in walls
        }

        # FIFO queue.
        queue = deque()
        queue.append((start, []))
        reached = {start}
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                if neighbor not in reached:
                    reached.add(neighbor)
                    new_path = path + [action]
                    queue.append((neighbor, new_path))
        return None

    # Lab 03 -Step 1.2.4 - DEPTH-FIRST SEARCH
    def dfs_search(self, start, goal, walls, grid_size):
        """DFS uses a LIFO stack.
        DFS does not guarantee the shortest path."""

        start = tuple(start)
        goal = tuple(goal)
        walls = {
            tuple(wall)
            for wall in walls
        }

        # LIFO stack.
        stack = []
        stack.append((start, []))
        reached = {start}
        while stack:
            current, path = stack.pop()
            if current == goal:
                return path
            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                if neighbor not in reached:
                    reached.add(neighbor)
                    new_path = path + [action]
                    stack.append((neighbor, new_path))
        return None

    # Lab 03 - Step 1.2.5 - UNIFORM-COST SEARCH
    def ucs_search(self, start, goal, walls, grid_size):
        """UCS expands the state with the lowest path cost.
        In this environment: Every movement = cost 1
        Therefore, UCS normally finds the same shortest path length as BFS.
        """

        start = tuple(start)
        goal = tuple(goal)
        walls = {
            tuple(wall)
            for wall in walls
        }

        frontier = []
        counter = 0
        heapq.heappush(
            frontier,
            (0, counter, start, [])
        )
        reached = {start: 0}
        while frontier:
            cost, _, current, path = heapq.heappop(frontier)
            if current == goal:
                return path
            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                new_cost = cost + 1
                if (neighbor not in reached
                    or new_cost < reached[neighbor]):
                    reached[neighbor] = new_cost
                    counter += 1
                    new_path = path + [action]
                    heapq.heappush(
                        frontier,
                            (new_cost,
                            counter,
                            neighbor,
                            new_path)
                    )
        return None

    # Lab 04 - Step 1.2.1 - A* SEARCH
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan', 
        tile_percepts=None # Lab 05 - Step 3.2 
    ):
        """A* Search combines:
            g(n) = cost from start to current node
            h(n) = estimated cost from current node to goal
            f(n) = g(n) + h(n)
        A* selects the node with the lowest f(n)."""

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = {tuple(wall) for wall in walls}
        tile_percepts = tile_percepts or {} # Lab 05 - Step 3.2 

        # Lab 04 - Select the heuristic function.
        # Manhattan is the default because this environment allows only four-way movement.
        if heuristic_type.lower() == 'manhattan':
            heuristic = self.manhattan_distance
        elif heuristic_type.lower() == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            raise ValueError("Unknown heuristic type.Use 'manhattan' or 'euclidean'.")

        # Lab 04 - Step 1.2.2 - Initialize the A* priority queue.
        # Tuple format:(f_cost, g_cost, current_pos, path_taken)
        frontier = []
        initial_g = 0
        initial_h = heuristic(start_pos,goal_pos)
        initial_f = initial_g + initial_h
        counter = 0  # The counter prevents heap comparison problems if two nodes have equal f and g costs.

        heapq.heappush(
            frontier,
            (initial_f, initial_g, counter, start_pos, [])
        )

        # Lab 04 - Step 1.2.2 - reached_states stores states that have already been processed.
        reached_states = set()
        # Lab 04 - Step 1.2.3,1.2.4 - A* main search loop
        while frontier:
            (
                f_cost,
                g_cost,
                _,
                current_pos,
                path_taken
            ) = heapq.heappop(frontier)

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Skip a state that has already been expanded.
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            # Lab 04 - Step 1.2.5 - Expand all valid neighboring states.
            for neighbor, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):
                if neighbor in reached_states:
                    continue

                # Lab 05 - Step 3.2 - Knowledge Base feasibility check
                self.kb.clear_facts()
                for fact in tile_percepts.get(neighbor, []): # Add percepts for this tile
                    self.kb.tell_fact(fact)
                self.kb.forward_chain() # Apply forward chaining
                if "Retreat" in self.kb.facts: # If Retreat is deduced, skip this tile
                    continue

                new_g = g_cost + 1  # g(n): actual cost from start to neighbor
                new_h = heuristic(  # h(n): estimated cost from neighbor to goal
                    neighbor, 
                    goal_pos
                )
                new_f = new_g + new_h  # f(n) = g(n) + h(n)
                new_path = path_taken + [action]
                counter += 1
                # Add the new state to the priority queue.
                heapq.heappush(
                    frontier,
                    (
                        new_f,
                        new_g,
                        counter,
                        neighbor,
                        new_path
                    )
                )

        # No path was found.
        return None

    # Lab 03, 04 - SEARCH DISPATCHER
    def search(self, start, goal, walls, grid_size, tile_percepts=None):
        """Select and execute the requested search algorithm."""
        if self.active_algo == "BFS":
            return self.bfs_search(
                start,
                goal,
                walls,
                grid_size
            )
        elif self.active_algo == "DFS":
            return self.dfs_search(
                start,
                goal,
                walls,
                grid_size
            )
        elif self.active_algo == "UCS":
            return self.ucs_search(
                start,
                goal,
                walls,
                grid_size
            )
        
        # Lab 04 - Step 1.3.2 A* Search option.
        # self.active_algo is converted to uppercase in __init__, therefore "AStar" becomes "ASTAR".
        elif self.active_algo == "ASTAR":
            return self.astar_search(
                start,
                goal,
                walls,
                grid_size,
                heuristic_type="manhattan",
                tile_percepts=tile_percepts # Lab 05 - Step 3.2
            )
        
        else:
            raise ValueError(f"Unknown search algorithm: {self.active_algo}")

    # Lab 03 - SENSE AND ACT
    def sense_and_act(self, percept):
        """Agent program.
        The agent:
            1. Checks whether food is at the current position.
            2. If yes, collects it.
            3. If there is no plan, creates a search plan.
            4. Executes one action from the plan."""

        # Collect food if the agent is already standing on a food position.
        if percept["food_here"]:
            self.plan = []
            return "Collect"
        
        # If there is no existing plan, create a new plan.
        if not self.plan:
            start = tuple(percept["agent_pos"])
            grid_size = percept["grid_size"]
            walls = { tuple(wall) for wall in percept["walls"] }
            all_food = { tuple(food) for food in percept["all_food"] }
            if not all_food:
                return "Collect"
            
            # Lab 04 - Step 1.3.4 - Select the closest food as the A* goal.
            goal = min(
                all_food,
                key=lambda food:
                    abs(start[0] - food[0]) + abs(start[1] - food[1])
            )

            # Lab 05 - Step 3.2 - Pass tile percepts to search for logical feasibility checks
            tile_percepts = percept.get("tile_percepts", {})
            
            self.plan = self.search(
                start,
                goal,
                walls,
                grid_size,
                tile_percepts=tile_percepts # Lab 05 - Step 3.2
            )
            if self.plan is None:
                self.plan = []

            # Display search information in terminal.
            print("Algorithm :", self.active_algo)
            print("Start     :", start)
            print("Goal      :", goal)
            print("Plan      :", self.plan)
            print("Path Cost :", len(self.plan))

        # Execute the next planned action.
        if self.plan:
            return self.plan.pop(0)

        # No path available.
        return "Collect"


# Lab 04 - Step 1.1 Testing Checkpoint
if __name__ == "__main__":
    test_agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)

    print("Manhattan Distance:", test_agent.manhattan_distance(start, goal))
    print("Euclidean Distance:", test_agent.euclidean_distance(start, goal))