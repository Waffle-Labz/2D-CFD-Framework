def Ellipse(width, height):
    shape = []

    for y in range(height):
        row = ""

        for x in range(width):
            # Centre of the ellipse
            cx = (width - 1) / 2
            cy = (height - 1) / 2

            # Normalised coordinates
            dx = (x - cx) / (width / 2)
            dy = (y - cy) / (height / 2)

            if dx**2 + dy**2 <= 1:
                row += "1"
            else:
                row += "0"

        shape.append(row)

    return shape

def Circle(radius):
    return Ellipse(radius * 2, radius * 2)