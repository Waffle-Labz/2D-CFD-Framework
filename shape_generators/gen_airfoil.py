# Generates NACAmptt of with chord
import math

def Airfoil(chord, m, p, t, angle_of_attack=0):
    heights = []
    angle_of_attack *= -1

    # Convert NACA digits from percentages to fractions
    m /= 100
    p /= 10
    t /= 100

    for x in range(chord + 1):
        # Normalised x coordinate: 0 at leading edge, 1 at trailing edge
        x_norm = x / chord

        # Thickness distribution
        yt = 5 * t * (
            0.2969 * math.sqrt(x_norm)
            - 0.1260 * x_norm
            - 0.3516 * x_norm**2
            + 0.2843 * x_norm**3
            - 0.1015 * x_norm**4
        )

        # Camber line
        if m == 0:
            yc = 0
            dyc_dx = 0

        elif x_norm < p:
            yc = (m / p**2) * (2 * p * x_norm - x_norm**2)
            dyc_dx = (2 * m / p**2) * (p - x_norm)

        else:
            yc = (m / (1 - p)**2) * (
                (1 - 2 * p) + 2 * p * x_norm - x_norm**2
            )
            dyc_dx = (2 * m / (1 - p)**2) * (p - x_norm)

        # Angle of the camber line
        theta = math.atan(dyc_dx)

        # Upper and lower surface coordinates
        xu = x_norm - yt * math.sin(theta)
        yu = yc + yt * math.cos(theta)

        xl = x_norm + yt * math.sin(theta)
        yl = yc - yt * math.cos(theta)

        # Convert to simulation/grid coordinates
        upper_height = yu * chord
        lower_height = yl * chord

        heights.append((upper_height, lower_height))

    # ---------------------------------------------------------
    # ORIGINAL METHOD — AoA = 0
    # ---------------------------------------------------------

    if angle_of_attack == 0:

        # Shift the whole airfoil upwards so its minimum y = 0
        min_height = min(lower for _, lower in heights)

        heights = [
            (upper - min_height, lower - min_height)
            for upper, lower in heights
        ]

        max_height = math.ceil(max(upper for upper, _ in heights))

        foil = [
            ["0" for _ in range(chord + 1)]
            for _ in range(max_height + 1)
        ]

        for x, (upper, lower) in enumerate(heights):
            upper = round(upper)
            lower = round(lower)

            for y in range(lower, upper + 1):
                if 0 <= y < len(foil):
                    foil[y][x] = "1"

        # Grid is currently bottom-to-top, so reverse it
        foil.reverse()

        return ["".join(row) for row in foil]

    # ---------------------------------------------------------
    # ROTATED METHOD — AoA != 0
    # ---------------------------------------------------------

    alpha = math.radians(angle_of_attack)

    # Convert airfoil into individual grid points
    points = []

    for x, (upper, lower) in enumerate(heights):
        for y in range(round(lower), round(upper) + 1):
            points.append((x, y))

    # Centre of the airfoil
    centre_x = chord / 2
    centre_y = (
        max(y for _, y in points) +
        min(y for _, y in points)
    ) / 2

    rotated_points = []

    for x, y in points:

        # Move centre to origin
        x -= centre_x
        y -= centre_y

        # Rotate
        rotated_x = (
            x * math.cos(alpha)
            - y * math.sin(alpha)
        )

        rotated_y = (
            x * math.sin(alpha)
            + y * math.cos(alpha)
        )

        # Move back
        rotated_x += centre_x
        rotated_y += centre_y

        rotated_points.append((rotated_x, rotated_y))

    # Shift so minimum coordinates are positive
    min_x = min(x for x, _ in rotated_points)
    min_y = min(y for _, y in rotated_points)

    rotated_points = [
        (
            round(x - min_x),
            round(y - min_y)
        )
        for x, y in rotated_points
    ]

    # Determine required grid size
    max_x = max(x for x, _ in rotated_points)
    max_y = max(y for _, y in rotated_points)

    foil = [
        ["0" for _ in range(max_x + 1)]
        for _ in range(max_y + 1)
    ]

    # Fill solid cells
    for x, y in rotated_points:
        foil[y][x] = "1"

    # Grid is currently bottom-to-top
    foil.reverse()
    foil = clean_shape(foil)
    foil = clean_shape(foil)

    return ["".join(row) for row in foil]

def clean_shape(shape):
    height = len(shape)
    width = len(shape[0])

    grid = [list(row) for row in shape]

    # Fill isolated holes inside solid
    for y in range(1, height - 1):
        for x in range(1, width - 1):

            if grid[y][x] == "0":
                neighbours = [
                    grid[y - 1][x],
                    grid[y + 1][x],
                    grid[y][x - 1],
                    grid[y][x + 1]
                ]

                # If surrounded by solid, fill the hole
                if neighbours.count("1") >= 3:
                    grid[y][x] = "1"

    # Remove isolated solid cells
    for y in range(1, height - 1):
        for x in range(1, width - 1):

            if grid[y][x] == "1":
                neighbours = [
                    grid[y - 1][x],
                    grid[y + 1][x],
                    grid[y][x - 1],
                    grid[y][x + 1]
                ]

                # If almost completely surrounded by fluid,
                # remove the isolated cell
                if neighbours.count("1") <= 1:
                    grid[y][x] = "0"

    return ["".join(row) for row in grid]

# airfoil = generate_airfoil(100, 0, 0, 12)
# airfoil = generate_airfoil(60, 2,4,12)
