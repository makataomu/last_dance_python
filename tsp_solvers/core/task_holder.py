class TSPInstance:
    def __init__(self, name, comment, dimension, coords, float_dist: bool = True):
        """
        Initialize the TSP Instance.

        Parameters
        ----------
        name : str
            The name of the TSP instance.
        comment : str
            Any comment or description about the instance.
        dimension : int
            Number of cities.
        coords : list of (float, float)
            A list of tuples (x, y) representing city coordinates.
        """
        self.name = name
        self.comment = comment
        self.dimension = dimension
        self.coords = coords
        self.float_dist = float_dist
        # We can precompute the distance matrix if desired
        self._distance_matrix = None

    @classmethod
    def from_file(cls, file_path, float_dist: bool = True):
        """
        Create a TSPInstance object from a TSPLIB-format file.

        Parameters
        ----------
        file_path : str
            The path to the TSP instance file.

        Returns
        -------
        TSPInstance
            A fully initialized TSP instance.
        """
        name = None
        comment_lines = []
        dimension = None
        coords = []

        reading_coords = False
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse known keywords
                if line.startswith("NAME:"):
                    name = line.split("NAME:")[1].strip()
                elif line.startswith("COMMENT"):
                    # We can accumulate all comments
                    comment_lines.append(line.split("COMMENT")[1].strip(': ').strip())
                elif line.startswith("TYPE:"):
                    # We might not strictly need to use this, but we can store if needed
                    # type_ = line.split("TYPE:")[1].strip()
                    pass
                elif line.startswith("DIMENSION:"):
                    dimension = int(line.split("DIMENSION:")[1].strip())
                elif line.startswith("EDGE_WEIGHT_TYPE:"):
                    # Typically: EDGE_WEIGHT_TYPE: EUC_2D
                    # We'll assume EUC_2D for now
                    pass
                elif "NODE_COORD_SECTION" in line:
                    # The next lines should be coordinates of each city
                    reading_coords = True
                    continue
                elif reading_coords:
                    # Parse coordinates: format is "<index> <x> <y>"
                    parts = line.split()
                    if len(parts) >= 3:
                        # Ignore the index since it's usually 1-based and we just store
                        x = float(parts[1])
                        y = float(parts[2])
                        coords.append((x, y))
                        if dimension and len(coords) == dimension:
                            # We have read all coordinates
                            break

        comment = "\n".join(comment_lines)

        # Validate that we got the expected number of coords
        if dimension is not None and len(coords) != dimension:
            raise ValueError(f"Expected {dimension} cities, but got {len(coords)}")

        return cls(name=name, comment=comment, dimension=dimension, coords=coords, float_dist=float_dist)

    def distance(self, i, j):
        """
        Compute Euclidean distance between city i and city j.

        Parameters
        ----------
        i : int
            Index of the first city (0-based)
        j : int
            Index of the second city (0-based)

        Returns
        -------
        float
            The Euclidean distance between city i and city j.
        """
        (x1, y1) = self.coords[i]
        (x2, y2) = self.coords[j]
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        if not self.float_dist:
            dist = int(dist)

        return dist

    @property
    def distance_matrix(self):
        """
        Compute (or return cached) full distance matrix for all cities.

        Returns
        -------
        list of list of float
            A 2D list (matrix) where element [i][j] is the distance
            from city i to city j.
        """
        if self._distance_matrix is None:
            self._distance_matrix = []
            for i in range(self.dimension):
                row = []
                for j in range(self.dimension):
                    if i == j:
                        row.append(0.0)
                    else:
                        d = self.distance(i, j)
                        row.append(d)
                self._distance_matrix.append(row)
        return self._distance_matrix

    def total_distance(self, route):
        """
        Compute the total distance of a given route.

        Parameters
        route : list of int
            A permutation of city indices representing the visiting order.
            For example: [0, 1, 2, ..., dimension-1]

        Returns
        -------
        float
            The total round-trip distance of the route.
        """
        dist = 0.0
        for idx in range(len(route)):
            current_city = route[idx]
            next_city = route[(idx + 1) % len(route)]
            dist += self.distance_matrix[current_city][next_city]
        return dist
