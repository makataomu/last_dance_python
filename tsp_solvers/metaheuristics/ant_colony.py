import random
from typing import Callable, List, Optional, Tuple

class AntColony:
    """
    Класс для решения задачи коммивояжера (TSP) с использованием метода муравьиной колонии (ACO).

    Args:
        num_ants:
            Количество муравьев в каждой итерации.
        alpha:
            Влияет на значимость феромонов при выборе пути. 
            Чем выше значение, тем большее значение придается феромонам.
        beta:
            Влияет на значимость расстояния при выборе пути. 
            Чем выше значение, тем большее значение придается близости городов.
        Q:
            Константа, используемая для определения количества феромонов, добавляемых на путь.
        evaporation:
            Коэффициент испарения феромонов. Значение должно быть между 0 и 1.
        max_iter:
            Максимальное количество итераций алгоритма.
        initial_pheromone_level:
            Начальный уровень феромонов на всех путях.
        stagnation_limit:
            Лимит итераций без улучшений, после которого феромоны сбрасываются.
        convergence_threshold:
            Порог, при котором алгоритм останавливается, если найденное решение 
            близко к оптимальному. Задается в процентах от optimal_cost.
        optimal_cost:
            Ожидаемая оптимальная стоимость маршрута. Используется вместе с convergence_threshold.
        verbose:
            Если True, выводит дополнительную информацию для отладки.
    """
    def __init__(
          self
        , num_ants               : int = 50
        , alpha                  : float = 2.0
        , beta                   : float = 4.0
        , Q                      : float = 100.0
        , evaporation            : float = 0.5
        , max_iter               : int = 1000
        , initial_pheromone_level: float = 0.1
        , stagnation_limit       : int = 50
        , convergence_threshold  : Optional[float] = None
        , optimal_cost           : Optional[float] = None
        , verbose                : bool = False
        ):
        
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

    def select_index(self, probabilities: List[float]) -> int:
        """
        Выбирает следующий город на основе переданных вероятностей.

        Args:
            probabilities:
                Список вероятностей для выбора следующего города.

        Returns:
            Индекс выбранного города.
        """
        random_value = random.random()
        cumulative_probability = 0.0
        for i, prob in enumerate(probabilities):
            cumulative_probability += prob
            if random_value <= cumulative_probability:
                return i
        return len(probabilities) - 1
    
    def reset_pheromones(self, best_path: Optional[List[int]], best_distance: Optional[float]):
        """
        Обновляет феромоны к initial_pheromone_level и ставит больше феромонов на лучший путь.

        Args:
            best_path: Лучший путь 
            best_distance: Лучшая длина
        """
        num_cities = len(self.pheromones)
        # Reset all pheromones to the initial level
        self.pheromones = [
            [self.initial_pheromone_level] * num_cities for _ in range(num_cities)
        ]

        # Apply enforced pheromone level on the best path if it exists
        if best_path and best_distance:
            pheromone_level = self.Q / best_distance
            for i in range(len(best_path) - 1):
                city_i = best_path[i]
                city_j = best_path[i + 1]
                self.pheromones[city_i][city_j] = pheromone_level
                self.pheromones[city_j][city_i] = pheromone_level

        if self.verbose:
            print("Pheromones have been reset and enforced on the best path.")

    def initialize(self, instance):
        num_cities = instance.dimension
        self.pheromones = [[self.initial_pheromone_level] * num_cities for _ in range(num_cities)]
        self.delta_pheromones = [[0.0] * num_cities for _ in range(num_cities)]
        self.current_iter = 0
        self.stagnation_count = 0
        self.best_path = None
        self.best_path_len = float('inf')
        self.reset_flag = False

    def solve_step(
          self
        , instance
        , on_iteration_callback: Optional[Callable[[int, List[int], float, List[List[float]]], None]] = None
        ) -> bool:
        """
        Решает задачу коммивояжера (TSP) с использованием метода муравьиной колонии (ACO).

        Args:
            instance:
                Объект задачи, который должен содержать атрибут dimension 
                (количество городов) и методы distance(i, j) для получения расстояния 
                между городами i и j, а также total_distance(path) для вычисления 
                длины пути.
            on_iteration_callback:
                Функция, вызываемая после каждой итерации. Принимает аргументы:
                - номер итерации,
                - лучший найденный путь,
                - длину лучшего пути,
                - текущую матрицу феромонов.
            callback_interval:
                Частота вызова on_iteration_callback (в итерациях).

        Returns:
            Кортеж из двух элементов:
            - лучший найденный путь (список индексов городов),
            - длина лучшего пути.
        """
        if self.current_iter >= self.max_iter:
            return False

        improved = False
        for ant in range(self.num_ants):
            current_path = [-1] * instance.dimension
            available_cities = list(range(instance.dimension))
            start_city = random.choice(available_cities)
            current_path[0] = start_city
            available_cities.remove(start_city)
            current_city = start_city

            while available_cities:
                probabilities = []
                sum_of_probabilities = 0.0
                for city in available_cities:
                    distance = instance.distance(current_city, city)
                    if distance == 0:
                        desirability = 0
                    else:
                        desirability = (self.pheromones[current_city][city] ** self.alpha) * (
                            (1 / distance) ** self.beta
                        )
                    probabilities.append(desirability)
                    sum_of_probabilities += desirability

                if sum_of_probabilities == 0:
                    # Avoid division by zero; choose randomly
                    next_city = random.choice(available_cities)
                else:
                    probabilities = [prob / sum_of_probabilities for prob in probabilities]
                    next_city_index = self.select_index(probabilities)
                    next_city = available_cities[next_city_index]

                current_path[len(current_path) - len(available_cities)] = next_city
                current_city = next_city
                available_cities.remove(next_city)

            path_length = instance.total_distance(current_path)
            if path_length < self.best_path_len:
                self.best_path = current_path[:]
                self.best_path_len = path_length
                improved = True

            pheromone_deposit = self.Q / path_length if path_length > 0 else 0
            for i in range(len(current_path) - 1):
                city_i = current_path[i]
                city_j = current_path[i + 1]
                self.delta_pheromones[city_i][city_j] += pheromone_deposit
                self.delta_pheromones[city_j][city_i] += pheromone_deposit

        # Update pheromones
        num_cities = instance.dimension
        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                self.pheromones[i][j] = (1 - self.evaporation) * self.pheromones[i][j] + self.delta_pheromones[i][j]
                self.pheromones[j][i] = self.pheromones[i][j]

        # Reset delta pheromones for the next iteration
        self.delta_pheromones = [[0.0] * num_cities for _ in range(num_cities)]

        if improved:
            self.stagnation_count = 0
        else:
            self.stagnation_count += 1

        if self.stagnation_count >= self.stagnation_limit:
            self.reset_pheromones(self.best_path, self.best_path_len)
            self.stagnation_count = 0

        self.current_iter += 1

        if on_iteration_callback and self.current_iter % 1 == 0:
            on_iteration_callback(self.current_iter, self.best_path, self.best_path_len, self.pheromones)

        # Check for convergence
        if self.convergence_threshold is not None and self.optimal_cost is not None:
            if self.best_path_len <= self.optimal_cost * (1 + self.convergence_threshold):
                return False

        # Check if maximum iterations reached
        if self.current_iter >= self.max_iter:
            return False

        return True

    def solve(
          self
        , instance
        , on_iteration_callback: Optional[Callable[[int, List[int], float, List[List[float]]], None]] = None
        , callback_interval: int = 1
        ) -> Tuple[List[int], float]:
        
        self.initialize(instance)

        for _ in range(self.max_iter):
            continue_solving = self.solve_step(instance, on_iteration_callback)
            if not continue_solving:
                break

        return self.best_path, self.best_path_len