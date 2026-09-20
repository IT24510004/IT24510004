# visual_grid_game.py
import random
import tkinter as tk
import os

from agent import SearchAgent
from PIL import Image, ImageTk

class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.direction = 'Up' # Lab 2 - Step 1.1
        
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        #Lab 1 - Step 2.1: Generate toxic traps
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:   # Create 5 traps
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap = (tx, ty)

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
            ):
                self.toxic_traps.add(trap)
                
        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if (
                tuple(op_pos) != (0, 0) 
                and tuple(op_pos) not in self.walls 
                and tuple(op_pos) not in self.food_positions 
                and tuple(op_pos) not in self.toxic_traps 
                and tuple(op_pos) not in [tuple(op) for op in self.opponents]
            ):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        # Lab 2 - Step 1.1: Setting the Trap (Partial Observability)
        x, y = self.agent_pos
        ahead_pos = [x, y]
    
        if self.direction == 'Up':
            ahead_pos[1] = min(self.height - 1, y + 1)
        elif self.direction == 'Down':
            ahead_pos[1] = max(0, y - 1)
        elif self.direction == 'Left':
            ahead_pos[0] = max(0, x - 1)
        elif self.direction == 'Right':
            ahead_pos[0] = min(self.width - 1, x + 1)
    
        ahead_tuple = tuple(ahead_pos)

        return {
            'agent_pos': list(self.agent_pos),
            #'opponent_positions': [list(op) for op in self.opponents],
            'wall_ahead': ahead_tuple in self.walls,
            'food_ahead': ahead_tuple in self.food_positions,
            'toxin_ahead': ahead_tuple in self.toxic_traps,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'toxin_here': tuple(self.agent_pos) in self.toxic_traps, #Lab 1 - Step 2.2: Add smells_toxin
            #'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),
            # Lab 03 - Step 1.1: Exposing the World Model
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action in ['Up', 'Down', 'Left', 'Right']:
            self.direction = action

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Lab 1 - Step 2.3:Toxic trap penalty
        if tuple_pos in self.toxic_traps:
            self.score -= 15
            
        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])

            new_op = list(op)

            if move == 'Up' and op[1] < self.height - 1:
                new_op[1] += 1
            elif move == 'Down' and op[1] > 0:
                new_op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                new_op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                new_op[0] += 1

            # Move only if the new position is not a wall
            if tuple(new_op) not in self.walls:
                op[0] = new_op[0]
                op[1] = new_op[1]

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


# Lab 2 - Step 1.2: The Simple Reflex Agent (Implementation & Failure)
class SimpleReflexAgent:
    """A simple reflex agent that acts purely on current percepts using IF-THEN rules."""

    def sense_and_act(self, percept: dict) -> str:
        # IF food is here THEN stay
        if percept.get('food_here'):
            return 'Stay'

        # IF wall is ahead THEN turn left
        elif percept.get('wall_ahead'):
            return 'Left'

        # ELSE move forward
        else:
            return 'Up'


# Lab 2 - Step 1.3: The Model-Based Agent
class ModelBasedAgent:
    """A model-based agent that uses memory of visited cells."""

    def __init__(self):
        # Internal memory
        self.visited_cells = set()

        # Remember the last action
        self.last_action = None

    def sense_and_act(self, percept: dict, walls: set) -> str:

        # 1. UPDATE INTERNAL STATE

        # Get the current position from the percept
        current_position = tuple(percept['agent_pos'])

        # Remember the current cell
        self.visited_cells.add(current_position)

        # 2. CHECK MEMORY

        x, y = current_position

        # Cell to the left
        left_cell = (x - 1, y)

        # Check whether left cell was already visited
        left_is_visited = left_cell in self.visited_cells

        # 3. IF-THEN RULES

        # IF food is here THEN stay
        if percept.get('food_here'):
            action = 'Stay'

        else:
            # Possible movements
            possible_moves = {
                'Up': (x, y + 1),
                'Down': (x, y - 1),
                'Left': (x - 1, y),
                'Right': (x + 1, y)
            }

            # Find cells that have NOT been visited
            unvisited_moves = []

            for move, position in possible_moves.items():

                # Check whether position is inside the grid
                inside_grid = (
                    0 <= position[0] < 12 and
                    0 <= position[1] < 12
                )

                # Check whether position is not a wall
                not_wall = position not in walls

                # Check whether position was not visited
                not_visited = position not in self.visited_cells

                if inside_grid and not_wall and not_visited:
                    unvisited_moves.append(move)

            # If there are unvisited cells,
            # randomly choose one
            if unvisited_moves:
                action = random.choice(unvisited_moves)

            # If all neighbouring cells were visited,
            # choose a random valid movement
            else:
                valid_moves = []

                for move, position in possible_moves.items():

                    inside_grid = (
                        0 <= position[0] < 12 and
                        0 <= position[1] < 12
                    )

                    not_wall = position not in walls

                    if inside_grid and not_wall:
                        valid_moves.append(move)

                if valid_moves:
                    action = random.choice(valid_moves)
                else:
                    action = 'Stay'

        # 4. REMEMBER LAST ACTION
        
        self.last_action = action

        return action
    
    
class GridGameGUI:
    """Tkinter GUI for the scalable multi-agent grid hunt game."""

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")


        # CREATE GAME ENVIRONMENT
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        #self.agent = SimpleReflexAgent() # Lab 2 - Step 1.2

        #self.agent = ModelBasedAgent()  # Lab 2 - Step 1.3
        
        #self.agent = SearchAgent(search_type='BFS')  # Lab 03 - Step 1.3

        self.agent = SearchAgent(search_type='A*')  # Lab 04 - Step 1.3

        # CALCULATE CELL SIZE
        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )


        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to assests folder
        assests_dir = os.path.join(base_dir, "assests")

        # LOAD PNG IMAGES
        self.agent_image = ImageTk.PhotoImage(
            Image.open(
                os.path.join(assests_dir, "agent.png")
            ).resize(
                (
                    int(self.cell_size * 0.7),
                    int(self.cell_size * 0.7)
                )
            )
        )

        self.opponent_image = ImageTk.PhotoImage(
            Image.open(
                os.path.join(assests_dir, "opponent.png")
            ).resize(
                (
                    int(self.cell_size * 0.7),
                    int(self.cell_size * 0.7)
                )
            )
        )

        self.toxic_image = ImageTk.PhotoImage(
            Image.open(
                os.path.join(assests_dir, "toxic_trap.png")
            ).resize(
                (
                    int(self.cell_size * 0.6),
                    int(self.cell_size * 0.6)
                )
            )
        )

        self.fruit_image = ImageTk.PhotoImage(
            Image.open(
                os.path.join(assests_dir, "fruit.png")
            ).resize(
                (
                    int(self.cell_size * 0.6),
                    int(self.cell_size * 0.6)
                )
            )
        )

  
        # CREATE CANVAS
        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )

        self.canvas.pack()

        # SCORE LABEL
        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Segoe UI", 14)
        )

        self.label.pack(pady=10)

        # START BUTTON
        
        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Segoe UI", 12),
            bg="#5C4E6F",
            fg="white"
        )

        self.btn.pack(pady=5)

        # Draw initial board
        self.draw_grid()


    # DRAW GAME BOARD

    def draw_grid(self):
        """Draw the grid, walls, food, toxic traps, opponents and agent."""

        # Clear previous drawing
        self.canvas.delete("all")

     
        # DRAW GRID AND WALLS
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * self.cell_size

                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Normal cell or wall
                if (x, y) in self.env.walls:
                    color = "#455A64"
                else:
                    color = "#F3E5F5"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#E1BEE7"
                )

                # Display W on walls if cell is large enough
                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )


        # DRAW FOOD
        for fx, fy in self.env.food_positions:

            x = (
                fx * self.cell_size
                + self.cell_size / 2
            )

            y = (
                (self.env.height - 1 - fy)
                * self.cell_size
                + self.cell_size / 2
            )

            self.canvas.create_image(
                x,
                y,
                image=self.fruit_image
            )

       
        # DRAW TOXIC TRAPS
        for tx, ty in self.env.toxic_traps:

            x = (
                tx * self.cell_size
                + self.cell_size / 2
            )

            y = (
                (self.env.height - 1 - ty)
                * self.cell_size
                + self.cell_size / 2
            )

            self.canvas.create_image(
                x,
                y,
                image=self.toxic_image
            )


        # DRAW OPPONENTS
        for ox, oy in self.env.opponents:

            x = (
                ox * self.cell_size
                + self.cell_size / 2
            )

            y = (
                (self.env.height - 1 - oy)
                * self.cell_size
                + self.cell_size / 2
            )

            self.canvas.create_image(
                x,
                y,
                image=self.opponent_image
            )


        # DRAW AGENT
        ax, ay = self.env.agent_pos

        x = (
            ax * self.cell_size
            + self.cell_size / 2
        )

        y = (
            (self.env.height - 1 - ay)
            * self.cell_size
            + self.cell_size / 2
        )

        self.canvas.create_image(
            x,
            y,
            image=self.agent_image
        )

    # RUN GAME
    def run_loop(self):
        """Run the game simulation."""

        # Disable button while game is running
        self.btn.config(state="disabled")

        def step():

            # Continue while game is not finished
            if not self.env.is_done():

                # Random movement for the agent
                #action = random.choice(
                #    [
                #        "Up",
                #        "Down",
                #        "Left",
                #        "Right"
                #    ]
                #)

                # Lab 2 - Step 1.3: The Model-Based Agent
                percept = self.env.get_percept()
                #action = self.agent.sense_and_act(percept, self.env.walls)

                # Lab 03 - Step 1.3: The Search Agent
                action = self.agent.sense_and_act(percept)

                # Execute action
                self.env.execute_action(action)

                # Redraw the board
                self.draw_grid()

                # Update information
                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )

                # Run next step after 250 milliseconds
                self.root.after(250, step)

            else:

                # Game ended because of collision
                if self.env.collision:

                    end_text = (
                        f"Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )

                # Game ended normally
                else:

                    end_text = (
                        f"Finished! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(text=end_text)

                # Enable button again
                self.btn.config(state="normal")

        # Start first step
        step()


# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=3)
    root.mainloop()