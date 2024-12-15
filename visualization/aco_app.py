import tkinter as tk

class AntColonyApp:
    def __init__(self, master, instance, solver):
        self.master = master
        self.instance = instance
        self.solver = solver

        # Flag to control the solver
        self.running = False

        # Main layout: left canvas for visualization, right frame for inputs
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side="left", padx=10, pady=10)

        self.input_frame = tk.Frame(master)
        self.input_frame.pack(side="right", padx=10, pady=10, fill="y")

        # Canvas for visualization
        self.canvas_size = 600
        self.padding = 50
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        # Inputs for parameters
        self.create_input_fields()

        # Start and Stop buttons
        self.start_button = tk.Button(self.input_frame, text="Start", command=self.start_solver)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.input_frame, text="Stop", command=self.stop_solver, state="disabled")
        self.stop_button.pack(pady=10)

        # Coordinates and scaling
        self.coords = instance.coords
        self.scaled_coords = self.scale_coords(self.coords)

        # Initial drawing
        self.draw_pheromones([[self.solver.initial_pheromone_level]*len(self.coords)]*len(self.coords))
        self.draw_cities()

    def scale_coords(self, coords):
        x_coords = [x for x, y in coords]
        y_coords = [y for x, y in coords]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        def scale(val, min_val, max_val):
            return self.padding + (val - min_val) / (max_val - min_val) * (self.canvas_size - 2 * self.padding)

        return [(scale(x, min_x, max_x), scale(y, min_y, max_y)) for x, y in coords]

    def draw_cities(self):
        for x, y in self.scaled_coords:
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")

    def draw_path(self, path, color="red", width=2):
        if not path:
            return
        for i in range(len(path)):
            city_a = self.scaled_coords[path[i]]
            city_b = self.scaled_coords[path[(i + 1) % len(path)]]
            self.canvas.create_line(city_a[0], city_a[1], city_b[0], city_b[1], fill=color, width=width)

    def draw_pheromones(self, pheromones):
        self.canvas.delete("pheromone")
        num_cities = len(pheromones)
        max_pheromone = max(max(row) for row in pheromones) if pheromones else 1
        min_pheromone = min(min(row) for row in pheromones) if pheromones else 0

        if max_pheromone == min_pheromone:
            max_pheromone += 1  # Prevent division by zero

        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                if pheromones[i][j] > 0:
                    city_a = self.scaled_coords[i]
                    city_b = self.scaled_coords[j]
                    # Normalize pheromone intensity between 0 and 255
                    intensity = int(255 * (pheromones[i][j] - min_pheromone) / (max_pheromone - min_pheromone))
                    intensity = max(0, min(255, intensity))  # Clamp to [0, 255]
                    color = f"#FF{255 - intensity:02x}FF"  # Example color mapping
                    line_width = 1 + int(3 * (pheromones[i][j] - min_pheromone) / (max_pheromone - min_pheromone))
                    self.canvas.create_line(
                        city_a[0], city_a[1], city_b[0], city_b[1],
                        fill=color, width=line_width, tags="pheromone"
                    )

    def update_visuals(self, iteration, best_path, best_distance, pheromones):
        self.master.title(f"Iteration {iteration}, Best Distance: {best_distance:.2f}")
        self.canvas.delete("all")
        self.draw_pheromones(pheromones)  # Draw pheromone trails first
        self.draw_cities()  # Draw cities on top
        self.draw_path(best_path, width=2, color='black')  # Draw the best path last

    def create_input_fields(self):
        tk.Label(self.input_frame, text="ACO Parameters", font=("Arial", 14, "bold")).pack(pady=5)

        self.param_vars = {}
        params = [
            ("Number of Ants", "num_ants", 50),
            ("Alpha (Pheromone Weight)", "alpha", 2.0),
            ("Beta (Distance Weight)", "beta", 4.0),
            ("Q (Pheromone Strength)", "Q", 100.0),
            ("Evaporation Rate", "evaporation", 0.5),
            ("Max Iterations", "max_iter", 1000),
            ("Initial Pheromone Level", "initial_pheromone_level", 0.1),
            ("Stagnation Limit", "stagnation_limit", 50),
            ("Convergence Threshold", "convergence_threshold", ""),
            ("Optimal Cost", "optimal_cost", ""),
        ]

        for label, var_name, default in params:
            frame = tk.Frame(self.input_frame)
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=label, width=25, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default))
            tk.Entry(frame, textvariable=var, width=10).pack(side="right")
            self.param_vars[var_name] = var

    def parse_value(self, value):
        """Convert the input value to an appropriate type."""
        value = value.strip()  # Remove leading/trailing whitespace
        if value.lower() == "none" or value == "":
            return None  # Treat 'None' or empty string as None
        try:
            if "." in value:  # Check for float values
                return float(value)
            return int(value)  # Default to int if no decimal
        except ValueError:
            raise ValueError(f"Invalid input for parameter: {value}")

    def start_solver(self):
        if self.running:
            return  # Prevent multiple instances

        try:
            # Fetch parameters from input fields
            params = {key: self.parse_value(var.get()) for key, var in self.param_vars.items()}

            # Update solver parameters
            self.solver.num_ants = params["num_ants"]
            self.solver.alpha = params["alpha"]
            self.solver.beta = params["beta"]
            self.solver.Q = params["Q"]
            self.solver.evaporation = params["evaporation"]
            self.solver.max_iter = params["max_iter"]
            self.solver.initial_pheromone_level = params["initial_pheromone_level"]
            self.solver.stagnation_limit = params["stagnation_limit"]
            self.solver.convergence_threshold = params["convergence_threshold"]
            self.solver.optimal_cost = params["optimal_cost"]

            # Initialize the solver
            self.solver.initialize(self.instance)

            # Disable Start button and enable Stop button
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            # Set running flag
            self.running = True

            # Start the iterative solving process
            self.run_solver_step()

        except ValueError as e:
            tk.messagebox.showerror("Input Error", str(e))

    def run_solver_step(self):
        if not self.running:
            return

        continue_solving = self.solver.solve_step(
            self.instance,
            on_iteration_callback=self.update_visuals
        )

        if not continue_solving:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            return

        # Schedule the next iteration
        self.master.after(1, self.run_solver_step)

    def stop_solver(self):
        if not self.running:
            return
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def on_close(self):
        self.stop_solver()
        self.master.destroy()
