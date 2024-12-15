import random

class ParticleSwarmOptimization:
    def __init__(self, num_particles=20, max_iterations=100, stagnation_threshold=500):
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.stagnation_threshold = stagnation_threshold

    def get_velocity(self):
        return [(random.randint(0, self.num_cities - 1), random.randint(0, self.num_cities - 1)) for _ in range(3)]

    def apply_velocity(self, solution, velocity):
        new_solution = solution[:]
        for swap in velocity:
            a, b = swap
            new_solution[a], new_solution[b] = new_solution[b], new_solution[a]
        return new_solution

    def solve(self, instance, on_iteration_callback=None, callback_interval=1):
        self.num_cities = instance.dimension

        particles = [random.sample(range(self.num_cities), self.num_cities) for _ in range(self.num_particles)]
        velocities = [self.get_velocity() for _ in range(self.num_particles)]
        p_best_positions = particles[:]
        p_best_scores = [instance.total_distance(p) for p in particles]

        g_best_position = min(p_best_positions, key=lambda p: instance.total_distance(p))
        g_best_score = instance.total_distance(g_best_position)

        iteration = 0
        stagnation_count = 0

        while iteration < self.max_iterations and stagnation_count < self.stagnation_threshold:
            improvement = False
            for i in range(self.num_particles):
                new_solution = self.apply_velocity(particles[i], velocities[i])
                new_distance = instance.total_distance(new_solution)

                if new_distance < p_best_scores[i]:
                    p_best_positions[i] = new_solution
                    p_best_scores[i] = new_distance
                    improvement = True

                if new_distance < g_best_score:
                    g_best_position = new_solution
                    g_best_score = new_distance
                    improvement = True

                velocities[i] = self.get_velocity()
                particles[i] = new_solution

            if improvement:
                stagnation_count = 0
            else:
                stagnation_count += 1

            if on_iteration_callback and iteration % callback_interval == 0:
                on_iteration_callback(iteration, g_best_position, g_best_score)

            iteration += 1

        if on_iteration_callback:
            on_iteration_callback(iteration, g_best_position, g_best_score)

        return g_best_position, g_best_score