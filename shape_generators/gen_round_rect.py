def RoundedRectangle(width, height, radius):
    if radius < 0:
        raise ValueError("Radius cannot be negative.")

    if radius * 2 > width or radius * 2 > height:
        raise ValueError("Radius is too large for the rectangle.")

    shape = []

    for y in range(height):
        row = ""

        for x in range(width):
            # Distance from the nearest corner region
            if x < radius:
                cx = radius
            elif x >= width - radius:
                cx = width - radius - 1
            else:
                cx = x

            if y < radius:
                cy = radius
            elif y >= height - radius:
                cy = height - radius - 1
            else:
                cy = y

            # Inside the rounded corner
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                row += "1"
            else:
                row += "0"

        shape.append(row)

    return shape