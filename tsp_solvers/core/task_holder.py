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

                # If we're reading the NODE_COORD_SECTION
                if reading_coords:
                    parts = line.split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        x = float(parts[1])
                        y = float(parts[2])
                        coords.append((x, y))
                        if dimension and len(coords) == dimension:
                            break
                    continue

                # Try to parse known lines by splitting on ':'
                # This handles variations like "DIMENSION : 38"
                if ':' in line:
                    key_val = line.split(':', 1)
                    key = key_val[0].strip().upper()
                    value = key_val[1].strip()

                    if key == "NAME":
                        name = value
                    elif key == "COMMENT":
                        comment_lines.append(value)
                    elif key == "DIMENSION":
                        dimension = int(value)
                    elif key == "TYPE":
                        # We can store or ignore TYPE if we want
                        pass
                    elif key == "EDGE_WEIGHT_TYPE":
                        # Typically EUC_2D
                        pass
                    elif "NODE_COORD_SECTION" in key:
                        reading_coords = True
                        continue
                else:
                    # Some lines might not have ':'
                    # For example, the line with NODE_COORD_SECTION might appear alone
                    # Try to detect NODE_COORD_SECTION here as well
                    if "NODE_COORD_SECTION" in line.upper():
                        reading_coords = True
                        continue

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
