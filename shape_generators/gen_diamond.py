def Diamond(width, height):
    shape = []

    cx = (width - 1) / 2
    cy = (height - 1) / 2

    for y in range(height):
        row = ""

        for x in range(width):
            # Normalised distance from the centre
            dx = abs(x - cx) / (width / 2)
            dy = abs(y - cy) / (height / 2)

            if dx + dy <= 1:
                row += "1"
            else:
                row += "0"

        shape.append(row)

    return shape