def Wedge(width, height):
    shape = []

    for y in range(height):
        # Distance from the vertical centre
        distance = abs(y - (height - 1) / 2)

        # Width of the solid at this row
        row_width = round(
            1 + (width - 1) * (distance / ((height - 1) / 2))
        )

        # Centre the triangle vertically
        row = "0" * row_width

        # Pad on the right so every row has the same width
        row += "1" * (width - row_width)

        shape.append(row)

    return shape