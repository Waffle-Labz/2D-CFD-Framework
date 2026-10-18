import csv
import matplotlib.pyplot as plt

# FILE_PATH = "data/uniform_flow/data.csv"
FILE_PATH = "data/geometry/rectangle/data.csv"

X_AXIS = "FRAME"
Y_AXIS = "AVERAGE PRESSURE"
# Y_AXIS = "MIN SPEED"

with open(FILE_PATH, "r") as f:
    reader = csv.DictReader(f)
    data = list(reader)

x = [float(row[X_AXIS]) for row in data]
y = [float(row[Y_AXIS]) for row in data]

plt.plot(x, y, marker="o")

plt.xlabel(X_AXIS.title())
plt.ylabel(Y_AXIS.title())
plt.title(X_AXIS.title() + " vs " + Y_AXIS.title())

plt.grid()
plt.show()