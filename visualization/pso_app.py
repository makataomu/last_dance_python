import tkinter as tk

class ParticleSwormApp:
    def __init__(self, instance, solver):
        self.instance = instance
        self.solver = solver
        self.root = tk.Tk()
        self.root.title("TSP Solver Visualization")
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()
        self.margin = 50  # Margin around canvas

        # Scale the coordinates to fit within the canvas
        self.coords = self.scale_coordinates(instance.coords)

    def scale_coordinates(self, coords):
        """Scale coordinates to fit the canvas size."""
        max_x = max(c[0] for c in coords)
        max_y = max(c[1] for c in coords)
        min_x = min(c[0] for c in coords)
        min_y = min(c[1] for c in coords)

        # Compute scaling factors
        scale_x = (self.canvas_width - 2 * self.margin) / (max_x - min_x)
        scale_y = (self.canvas_height - 2 * self.margin) / (max_y - min_y)

        # Scale and shift coordinates
        scaled_coords = [
            (
                self.margin + (x - min_x) * scale_x,
                self.margin + (y - min_y) * scale_y
            ) for x, y in coords
        ]
        return scaled_coords

    def draw_cities(self):
        """Draw cities as points on the canvas."""
        for i, (x, y) in enumerate(self.coords):
            self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill="red", outline="black", tags="city"
            )
            self.canvas.create_text(x + 10, y, text=str(i), fill="blue", font=("Arial", 10))

    def draw_route(self, route):
        """Draw the route on the canvas."""
        self.canvas.delete("route")
        for i in range(len(route)):
            city_a = route[i]
            city_b = route[(i + 1) % len(route)]
            x1, y1 = self.coords[city_a]
            x2, y2 = self.coords[city_b]
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="blue", width=2, tags="route"
            )

    def update_visualization(self, iteration, best_solution, best_distance):
        """Update the visualization for the current best solution."""
        self.canvas.delete("iteration")
        self.draw_route(best_solution)
        self.canvas.create_text(
            self.canvas_width // 2, 20,
            text=f"Iteration: {iteration} | Best Distance: {best_distance:.2f}",
            fill="black", font=("Arial", 16), tags="iteration"
        )
        self.root.update()

    def solve_and_visualize(self):
        """Solve the TSP and visualize each iteration."""
        def iteration_callback(iteration, solution, distance):
            if iteration % 100 == 0:  # Update visualization every 100 iterations
                self.update_visualization(iteration, solution, distance)

        # Draw initial setup
        self.draw_cities()

        # Solve the TSP with visualization
        best_solution, best_distance = self.solver.solve(
            self.instance,
            on_iteration_callback=iteration_callback,
            callback_interval=1
        )

        # Display the final solution
        self.update_visualization("Final", best_solution, best_distance)
        print("Best Solution:", best_solution)
        print("Best Distance:", best_distance)

        self.root.mainloop()