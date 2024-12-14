import tkinter as tk
import math
import random
from tsp_solvers.metaheuristics.simulated_annealing import SimulatedAnnealing

class SimulatedAnnealingApp:
    def __init__(self, master, instance):
        self.master = master
        self.master.title("Simulated Annealing for TSP")

        self.instance = instance
        self.sa_solver = SimulatedAnnealing(initial_temp=1000, cooling_rate=0.999, stopping_temp=1e-8, max_iterations=100)

        self.coords = self.instance.coords
        self.canvas_size = 500
        self.padding = 50

        self.x_coords = [c[0] for c in self.coords]
        self.y_coords = [c[1] for c in self.coords]

        min_x, max_x = min(self.x_coords), max(self.x_coords)
        min_y, max_y = min(self.y_coords), max(self.y_coords)

        def scale(val, min_val, max_val):
            if max_val == min_val:
                return self.canvas_size // 2
            return self.padding + (val - min_val) / (max_val - min_val) * (self.canvas_size - 2*self.padding)

        self.scaled_coords = [(scale(x, min_x, max_x), scale(y, min_y, max_y)) for x, y in self.coords]

        # Main frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack()

        # Canvas on the left
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack(side="left", padx=10, pady=10)

        # Stats frame on the right
        self.stats_frame = tk.Frame(self.main_frame)
        self.stats_frame.pack(side="right", padx=10, pady=10, fill="y")

        # Variables for stats
        self.iteration_label_var = tk.StringVar()
        self.best_distance_label_var = tk.StringVar()
        self.temp_label_var = tk.StringVar()

        tk.Label(self.stats_frame, text="Statistics:", font=("Arial", 14, "bold")).pack(pady=5)
        self.iteration_label = tk.Label(self.stats_frame, textvariable=self.iteration_label_var, font=("Arial", 12))
        self.iteration_label.pack(pady=5)
        self.best_distance_label = tk.Label(self.stats_frame, textvariable=self.best_distance_label_var, font=("Arial", 12))
        self.best_distance_label.pack(pady=5)
        self.temp_label = tk.Label(self.stats_frame, textvariable=self.temp_label_var, font=("Arial", 12))
        self.temp_label.pack(pady=5)

        self.reset_temp_button = tk.Button(self.stats_frame, text="Reset Temperature", command=self.reset_temperature)
        self.reset_temp_button.pack(pady=5)

        # SA Parameter inputs
        tk.Label(self.stats_frame, text="SA Parameters:", font=("Arial", 14, "bold")).pack(pady=10)

        self.param_frame = tk.Frame(self.stats_frame)
        self.param_frame.pack(pady=5)

        tk.Label(self.param_frame, text="Initial Temp:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.initial_temp_var = tk.DoubleVar(value=1000)
        tk.Entry(self.param_frame, textvariable=self.initial_temp_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self.param_frame, text="Cooling Rate:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.cooling_rate_var = tk.DoubleVar(value=0.999)
        tk.Entry(self.param_frame, textvariable=self.cooling_rate_var, width=10).grid(row=1, column=1, padx=5, pady=2)

        tk.Label(self.param_frame, text="Stopping Temp:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.stopping_temp_var = tk.DoubleVar(value=1e-8)
        tk.Entry(self.param_frame, textvariable=self.stopping_temp_var, width=10).grid(row=2, column=1, padx=5, pady=2)

        tk.Label(self.param_frame, text="Max Iterations:").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.max_iterations_var = tk.IntVar(value=100)
        tk.Entry(self.param_frame, textvariable=self.max_iterations_var, width=10).grid(row=3, column=1, padx=5, pady=2)

        # Button frame
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.run_button = tk.Button(self.button_frame, text="Run SA", command=self.start_sa)
        self.run_button.pack(side="left", padx=5)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side="left", padx=5)

        self.resume_button = tk.Button(self.button_frame, text="Resume", command=self.resume)
        self.resume_button.pack(side="left", padx=5)

        self.best_solution = None
        self.best_distance = None
        self.paused = False
        self.stagnation_threshold = 500

        # State for incremental runs
        self.temp = self.sa_solver.initial_temp
        self.iteration = 0
        self.stagnation_count = 0
        self.current_solution = None
        self.current_distance = None

        # Initially no route drawn
        self.draw_points()
        self.update_stats_labels(iteration=0, best_distance=None, temp=None)

    def draw_points(self):
        self.canvas.delete("all")
        # Draw cities
        for (x, y) in self.scaled_coords:
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue")

        # Draw the best path if we have one
        if self.best_solution:
            for i in range(len(self.best_solution)):
                c1 = self.scaled_coords[self.best_solution[i]]
                c2 = self.scaled_coords[self.best_solution[(i+1) % len(self.best_solution)]]
                self.canvas.create_line(c1[0], c1[1], c2[0], c2[1], fill="red", width=2)

    def start_sa(self):
        self.paused = False

        # Update SA parameters based on user inputs
        self.sa_solver.initial_temp = self.initial_temp_var.get()
        self.sa_solver.cooling_rate = self.cooling_rate_var.get()
        self.sa_solver.stopping_temp = self.stopping_temp_var.get()
        self.sa_solver.max_iterations = self.max_iterations_var.get()

        # Initialize or re-initialize SA parameters
        n = self.instance.dimension
        self.current_solution = list(range(n))
        random.shuffle(self.current_solution)
        self.current_distance = self.instance.total_distance(self.current_solution)
        self.best_solution = self.current_solution[:]
        self.best_distance = self.current_distance
        self.temp = self.sa_solver.initial_temp
        self.iteration = 0
        self.stagnation_count = 0

        self.update_stats_labels(iteration=self.iteration, best_distance=self.best_distance, temp=self.temp)
        self.run_iteration_step()

    def pause(self):
        self.paused = True

    def resume(self):
        if self.paused:
            self.paused = False
            self.run_iteration_step()

    def reset_temperature(self):
        if self.sa_solver:
            self.temp = self.sa_solver.initial_temp
            self.update_stats_labels(iteration=self.iteration, best_distance=self.best_distance, temp=self.temp)

    def run_iteration_step(self):
        if self.paused:
            return

        # Stop condition
        if self.temp <= self.sa_solver.stopping_temp or self.stagnation_count >= self.stagnation_threshold:
            self.master.title(f"SA Completed! Best: {self.best_distance:.2f}")
            return

        # Perform one "outer iteration" of SA logic (similar to what solve does)
        # but in an incremental fashion. We replicate the logic from solve()
        stagnation = True
        for _ in range(self.sa_solver.max_iterations):
            new_solution = self.sa_solver.get_neighbor_2opt(self.current_solution)
            new_distance = self.instance.total_distance(new_solution)

            if new_distance < self.current_distance:
                self.current_solution = new_solution
                self.current_distance = new_distance
                if self.current_distance < self.best_distance:
                    self.best_distance = self.current_distance
                    self.best_solution = self.current_solution[:]
                    stagnation = False
            else:
                diff = self.current_distance - new_distance
                if random.random() < math.exp(diff / self.temp):
                    self.current_solution = new_solution
                    self.current_distance = new_distance

        if stagnation:
            self.stagnation_count += 1
        else:
            self.stagnation_count = 0

        self.iteration_callback(self.iteration, self.best_solution, self.best_distance)
        self.temp *= self.sa_solver.cooling_rate
        self.iteration += 1

        # Schedule the next step
        self.master.after(10, self.run_iteration_step)

    def iteration_callback(self, iteration, best_solution, best_distance):
        self.best_solution = best_solution
        self.best_distance = best_distance
        self.master.title(f"SA Iteration {iteration}, Best: {best_distance:.2f}")
        self.draw_points()
        self.update_stats_labels(iteration=iteration, best_distance=best_distance, temp=self.temp)
        self.master.update_idletasks()

    def update_stats_labels(self, iteration, best_distance, temp):
        self.iteration_label_var.set(f"Iteration: {iteration}")
        if best_distance is not None:
            self.best_distance_label_var.set(f"Best Distance: {best_distance:.2f}")
        else:
            self.best_distance_label_var.set("Best Distance: N/A")
        if temp is not None:
            self.temp_label_var.set(f"Temperature: {temp:.6f}")
        else:
            self.temp_label_var.set("Temperature: N/A")
