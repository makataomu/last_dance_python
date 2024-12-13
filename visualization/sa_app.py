import tkinter as tk
from tsp_solvers.metaheuristics.simulated_annealing import SimulatedAnnealing

class SimulatedAnnealingApp:
    def __init__(self, master, instance):
        self.master = master
        self.master.title("Simulated Annealing for TSP")

        self.instance = instance
        # Extract coordinates (scale them if needed for the canvas)
        self.coords = self.instance.coords

        # Determine a scaling or offset if your coordinates are large
        # For simplicity, let's just rescale them to fit in a 500x500 canvas.
        self.canvas_size = 500
        self.x_coords = [c[0] for c in self.coords]
        self.y_coords = [c[1] for c in self.coords]

        min_x, max_x = min(self.x_coords), max(self.x_coords)
        min_y, max_y = min(self.y_coords), max(self.y_coords)

        # Simple linear scaling to fit the cities within the canvas
        # Add a small padding
        self.padding = 50
        def scale_x(x):
            return self.padding + (x - min_x) / (max_x - min_x) * (self.canvas_size - 2*self.padding)
        def scale_y(y):
            return self.padding + (y - min_y) / (max_y - min_y) * (self.canvas_size - 2*self.padding)

        self.scaled_coords = [(scale_x(x), scale_y(y)) for x,y in self.coords]

        self.canvas = tk.Canvas(master, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        self.run_button = tk.Button(master, text="Run SA", command=self.run_sa)
        self.run_button.pack()

        self.best_solution = None
        self.best_distance = None

        self.draw_points()

    def draw_points(self):
        # Draw cities as blue circles
        self.canvas.delete("all")
        for (x, y) in self.scaled_coords:
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue")

        # If we have a best solution, draw the path
        if self.best_solution:
            for i in range(len(self.best_solution)):
                c1 = self.scaled_coords[self.best_solution[i]]
                c2 = self.scaled_coords[self.best_solution[(i+1) % len(self.best_solution)]]
                self.canvas.create_line(c1[0], c1[1], c2[0], c2[1], fill="red", width=2)

    def run_sa(self):
        # Create a Simulated Annealing solver
        sa_solver = SimulatedAnnealing(initial_temp=1000, cooling_rate=0.999, stopping_temp=1e-8, max_iterations=100)

        # Solve the instance
        best_solution, best_distance = sa_solver.solve(self.instance, on_iteration_callback=self.iteration_callback, callback_interval=5)
        print("Final best distance:", best_distance)
        print("Final best solution:", best_solution)

    def iteration_callback(self, iteration, best_solution, best_distance):
        self.best_solution = best_solution
        self.best_distance = best_distance
        self.master.title(f"SA Iteration {iteration}, Best: {best_distance:.2f}")
        self.draw_points()
        self.master.update_idletasks()