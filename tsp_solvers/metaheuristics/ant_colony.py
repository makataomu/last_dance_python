import random 

class AntColony:
    def __init__(self, 
                 num_ants=50, 
                 alpha=2.0, 
                 beta=4.0, 
                 Q=100.0, 
                 evaporation=0.5, 
                 max_iter=1000, 
                 initial_pheromone_level=0.1, 
                 stagnation_limit=50, 
                 convergence_threshold=None, 
                 optimal_cost=None, 
                 verbose=False):
        # Existing initialization
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.evaporation = evaporation
        self.max_iter = max_iter
        self.initial_pheromone_level = initial_pheromone_level
        self.stagnation_limit = stagnation_limit
        self.convergence_threshold = convergence_threshold
        self.optimal_cost = optimal_cost
        self.verbose = verbose

        # Store pheromone data for visualization
        self.pheromones = None

    def select_index(self, probabilities):
        """Select a city based on the given probabilities."""
        random_value = random.random()
        cumulative_probability = 0.0
        for i, prob in enumerate(probabilities):
            cumulative_probability += prob
            if random_value <= cumulative_probability:
                return i
        return len(probabilities) - 1

    def solve(self, instance, on_iteration_callback=None, callback_interval=1):
        """
        Solve the TSP using Ant Colony Optimization.
        """
        num_cities = instance.dimension
        self.pheromones = [[self.initial_pheromone_level] * num_cities for _ in range(num_cities)]
        delta_pheromones = [[0.0] * num_cities for _ in range(num_cities)]
        best_path = None
        best_path_len = float('inf')
        stagnation_count = 0

        for t in range(self.max_iter):
            improved = False
            for ant in range(self.num_ants):
                current_path = [-1] * num_cities
                available_cities = list(range(num_cities))
                start_city = random.choice(available_cities)
                current_path[0] = start_city
                available_cities.remove(start_city)
                current_city = start_city

                while available_cities:
                    probabilities = []
                    sum_of_probabilities = 0.0
                    for city in available_cities:
                        desirability = (self.pheromones[current_city][city] ** self.alpha) * (
                            (1 / instance.distance(current_city, city)) ** self.beta
                        )
                        probabilities.append(desirability)
                        sum_of_probabilities += desirability

                    probabilities = [prob / sum_of_probabilities for prob in probabilities]
                    next_city_index = self.select_index(probabilities)
                    next_city = available_cities[next_city_index]

                    current_path[len(current_path) - len(available_cities)] = next_city
                    current_city = next_city
                    available_cities.remove(next_city)

                path_length = instance.total_distance(current_path)
                if path_length < best_path_len:
                    best_path = current_path[:]
                    best_path_len = path_length
                    improved = True

                pheromone_deposit = self.Q / path_length
                for i in range(len(current_path) - 1):
                    city_i = current_path[i]
                    city_j = current_path[i + 1]
                    delta_pheromones[city_i][city_j] += pheromone_deposit
                    delta_pheromones[city_j][city_i] += pheromone_deposit

            for i in range(num_cities):
                for j in range(i + 1, num_cities):
                    self.pheromones[i][j] = (1 - self.evaporation) * self.pheromones[i][j] + delta_pheromones[i][j]
                    self.pheromones[j][i] = self.pheromones[i][j]

            delta_pheromones = [[0.0] * num_cities for _ in range(num_cities)]

            if improved:
                stagnation_count = 0
            else:
                stagnation_count += 1

            if stagnation_count >= self.stagnation_limit:
                self.pheromones = [[self.initial_pheromone_level] * num_cities for _ in range(num_cities)]
                stagnation_count = 0

            if on_iteration_callback and t % callback_interval == 0:
                on_iteration_callback(t, best_path, best_path_len, self.pheromones)

            if self.convergence_threshold is not None and self.optimal_cost is not None:
                if best_path_len <= self.optimal_cost * (1 + self.convergence_threshold):
                    break

        return best_path, best_path_len
