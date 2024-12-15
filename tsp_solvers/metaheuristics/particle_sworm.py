import random

class ParticleSwarmOptimization:
    """
    Particle Swarm Optimization (PSO) solver for the Traveling Salesman Problem (TSP).

    PSO is a metaheuristic optimization algorithm where a set of particles (solutions)
    move through the solution space to find a global optimum. Particles share information 
    about their best solutions to improve the swarm's overall performance.

    Attributes
    ----------
    num_particles : int
        Number of particles in the swarm.
    max_iterations : int
        Maximum number of iterations for the PSO algorithm.
    stagnation_threshold : int
        Number of iterations without improvement before stopping.
    """

    def __init__(self, num_particles=20, max_iterations=100, stagnation_threshold=500):
        """
        Initialize the PSO solver with the given parameters.

        Parameters
        ----------
        num_particles : int, optional
            Number of particles (candidate solutions) in the swarm. Default is 20.
        max_iterations : int, optional
            Maximum number of iterations before stopping. Default is 100.
        stagnation_threshold : int, optional
            Number of iterations without improvement to trigger early stopping. Default is 500.
        """
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.stagnation_threshold = stagnation_threshold

    def get_velocity(self):
        """
        Generate a random 'velocity' for a particle.

        The velocity is represented as a list of swap operations (pairs of indices),
        which will be applied to a solution to create a new one.

        Returns
        -------
        list of tuple of int
            A list of swap operations, where each tuple (a, b) represents indices to swap.
        """
        return [(random.randint(0, self.num_cities - 1), random.randint(0, self.num_cities - 1)) for _ in range(3)]

    def apply_velocity(self, solution, velocity):
        """
        Apply the 'velocity' (swap operations) to a given solution.

        Parameters
        ----------
        solution : list of int
            The current solution (a tour represented as a list of city indices).
        velocity : list of tuple of int
            A list of swap operations to apply to the solution.

        Returns
        -------
        list of int
            A new solution obtained after applying the velocity.
        """
        new_solution = solution[:]
        for swap in velocity:
            a, b = swap
            # Swap two cities in the tour
            new_solution[a], new_solution[b] = new_solution[b], new_solution[a]
        return new_solution

    def solve(self, instance, on_iteration_callback=None, callback_interval=1):
        """
        Solve the TSP instance using the Particle Swarm Optimization algorithm.

        Parameters
        ----------
        instance : TSPInstance
            An instance of the TSP problem containing city coordinates and a method 
            to compute the total distance of a route.
        on_iteration_callback : callable, optional
            A callback function to monitor progress. It receives the current iteration, 
            the best solution, and the best distance.
        callback_interval : int, optional
            Frequency of calling the callback function (e.g., every N iterations). Default is 1.

        Returns
        -------
        tuple
            A tuple containing the best solution (list of city indices) and its total distance (float).
        """
        self.num_cities = instance.dimension

        # Initialize particles and their velocities
        particles = [random.sample(range(self.num_cities), self.num_cities) for _ in range(self.num_particles)]
        velocities = [self.get_velocity() for _ in range(self.num_particles)]
        p_best_positions = particles[:]  # Personal best positions
        p_best_scores = [instance.total_distance(p) for p in particles]  # Personal best scores

        # Initialize the global best solution
        g_best_position = min(p_best_positions, key=lambda p: instance.total_distance(p))
        g_best_score = instance.total_distance(g_best_position)

        iteration = 0
        stagnation_count = 0

        # Main PSO loop
        while iteration < self.max_iterations and stagnation_count < self.stagnation_threshold:
            improvement = False
            for i in range(self.num_particles):
                # Apply velocity to the current solution
                new_solution = self.apply_velocity(particles[i], velocities[i])
                new_distance = instance.total_distance(new_solution)

                # Update personal best (pBest)
                if new_distance < p_best_scores[i]:
                    p_best_positions[i] = new_solution
                    p_best_scores[i] = new_distance
                    improvement = True

                # Update global best (gBest)
                if new_distance < g_best_score:
                    g_best_position = new_solution
                    g_best_score = new_distance
                    improvement = True

                # Generate a new velocity for the particle
                velocities[i] = self.get_velocity()

                # Update particle position
                particles[i] = new_solution

            # Check for stagnation
            if improvement:
                stagnation_count = 0
            else:
                stagnation_count += 1

            # Call the callback function to report progress
            if on_iteration_callback and iteration % callback_interval == 0:
                on_iteration_callback(iteration, g_best_position, g_best_score)

            iteration += 1

        # Final callback after the algorithm finishes
        if on_iteration_callback:
            on_iteration_callback(iteration, g_best_position, g_best_score)

        return g_best_position, g_best_score
