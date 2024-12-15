import tkinter as tk

class AntColonyApp:
    def __init__(self, master, instance, solver):
        self.master = master
        self.instance = instance
        self.solver = solver

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

        # Start button
        self.start_button = tk.Button(self.input_frame, text="Start", command=self.start_solver)
        self.start_button.pack(pady=10)

        # Coordinates and scaling
        self.coords = instance.coords
        self.scaled_coords = self.scale_coords(self.coords)

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
        for i in range(len(path)):
            city_a = self.scaled_coords[path[i]]
            city_b = self.scaled_coords[path[(i + 1) % len(path)]]
            self.canvas.create_line(city_a[0], city_a[1], city_b[0], city_b[1], fill=color, width=width)

    def draw_pheromones(self, pheromones):
        max_pheromone = max(max(row) for row in pheromones)  # Maximum pheromone value
        min_pheromone = min(min(row) for row in pheromones)  # Minimum pheromone value

        if max_pheromone == min_pheromone:  # Handle the edge case of all equal pheromones
            max_pheromone += 1

        min_intensity = 0
        for i in range(len(pheromones)):
            for j in range(i + 1, len(pheromones)):
                if pheromones[i][j] > 0:  # Only draw lines for positive pheromones
                    city_a = self.scaled_coords[i]
                    city_b = self.scaled_coords[j]
                    intensity = min_intensity + int(
                        (pheromones[i][j] - min_pheromone) / (max_pheromone - min_pheromone) * (255 - min_intensity)
                    )
                    intensity = 255 - intensity
                    color = f"#FF{intensity:02x}FF"
                    line_width = 1 + int(3 * (pheromones[i][j] - min_pheromone) / (max_pheromone - min_pheromone))
                    self.canvas.create_line(
                        city_a[0], city_a[1], city_b[0], city_b[1], fill=color, width=line_width
                    )

    def update_visuals(self, iteration, best_path, best_distance, pheromones):
        self.master.title(f"Iteration {iteration}, Best Distance: {best_distance:.2f}")
        self.canvas.delete("all")
        self.draw_pheromones(pheromones)  # Draw pheromone trails first
        self.draw_cities()  # Draw cities on top
        self.draw_path(best_path, width=1, color='black')  # Draw the best path last

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
            ("Convergence Threshold", "convergence_threshold", None),
            ("Optimal Cost", "optimal_cost", None),
        ]

        for label, var_name, default in params:
            frame = tk.Frame(self.input_frame)
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=label, width=25, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default))
            tk.Entry(frame, textvariable=var, width=10).pack(side="right")
            self.param_vars[var_name] = var

    def start_solver(self):
        # Fetch parameters from input fields
        def parse_value(value):
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

        params = {key: parse_value(var.get()) for key, var in self.param_vars.items()}

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

        def on_iteration_callback(iteration, best_path, best_distance, pheromones):
            self.update_visuals(iteration, best_path, best_distance, pheromones)
            self.master.update_idletasks()

        # Start solving
        self.solver.solve(self.instance, on_iteration_callback=on_iteration_callback, callback_interval=1)
