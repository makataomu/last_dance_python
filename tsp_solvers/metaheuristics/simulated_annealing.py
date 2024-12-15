import random
from ..utils import exp_manual

class SimulatedAnnealing:
    def __init__(self, 
                 initial_temp=1000.0, 
                 cooling_rate=0.999, 
                 stopping_temp=1e-8, 
                 max_iterations=100):
        """
        Initialize the Simulated Annealing solver.

        Parameters
        ----------
        initial_temp : float
            The initial temperature for SA.
        cooling_rate : float
            The factor by which the temperature is multiplied each iteration.
        stopping_temp : float
            The temperature below which the algorithm terminates.
        max_iterations : int
            The number of iterations (neighbor evaluations) per temperature level.
        """
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.stopping_temp = stopping_temp
        self.max_iterations = max_iterations

    def get_neighbor_2opt(self, tour):
        """
        Create a neighbor solution by performing a 2-opt swap on the tour.
        
        Parameters
        ----------
        tour : list of int
            Current tour (list of city indices).

        Returns
        -------
        list of int
            A new tour (neighbor) after a 2-opt swap.
        """
        new_tour = tour[:]
        i, j = sorted(random.sample(range(len(tour)), 2))
        new_tour[i:j+1] = reversed(new_tour[i:j+1])
        return new_tour

    def solve(self, instance, on_iteration_callback=None, callback_interval=1, stagnation_threshold=500, current_solution=None):
        n = instance.dimension

        if not current_solution:
            current_solution = list(range(n))
            random.shuffle(current_solution)
        current_distance = instance.total_distance(current_solution)

        best_solution = current_solution[:]
        best_distance = current_distance

        temp = self.initial_temp
        iteration = 0
        stagnation_count = 0

        # Loop until we either reach the stopping_temp or have stagnated for too long
        while (temp > self.stopping_temp) and (stagnation_count < stagnation_threshold):
            stagnation = True
            for _ in range(self.max_iterations):
                new_solution = self.get_neighbor_2opt(current_solution)
                new_distance = instance.total_distance(new_solution)

                if new_distance < current_distance:
                    current_solution = new_solution
                    current_distance = new_distance
                    if current_distance < best_distance:
                        best_distance = current_distance
                        best_solution = current_solution[:]
                        stagnation = False
                else:
                    diff = current_distance - new_distance
                    # Accept worse solution with a probability
                    if random.random() < exp_manual(diff / temp):
                        current_solution = new_solution
                        current_distance = new_distance
            
            if stagnation:
                stagnation_count += 1
            else:
                stagnation_count = 0

            # Every iteration (of the outer loop), we record/update via callback
            if on_iteration_callback and iteration % callback_interval == 0:
                on_iteration_callback(iteration, best_solution, best_distance)

            temp *= self.cooling_rate
            iteration += 1

        # Final callback after completion (optional)
        if on_iteration_callback:
            on_iteration_callback(iteration, best_solution, best_distance)

        return best_solution, best_distance
