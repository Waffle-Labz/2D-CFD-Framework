import csv
import matplotlib.pyplot as plt

# Path to any results.csv file
FILE_PATH = "benchmark/frame_count/results.csv"

# Header of csv column to plot on x-axis
X_AXIS = "frames"

# Header(s) of csv column(s) to plot on y-axis
Y_AXES = ["total_mean", "calc_mean", "render_mean"]

X_LABEL = "Frame Count"
Y_LABEL = "Mean Time per Frame (s)"
TITLE = "Benchmark Runtime vs Cell Count"

LOG_SCALE = True

Y_MIN = None
Y_MAX = None

with open(FILE_PATH, "r") as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Sort by x-axis value
data.sort(key=lambda row: int(row[X_AXIS]))

x = [int(row[X_AXIS]) for row in data]

for column in Y_AXES:
    y = [float(row[column]) for row in data]
    plt.plot(x, y, marker="o", label=column)

if LOG_SCALE:
    plt.xscale("log")

if Y_MIN is not None or Y_MAX is not None:
    plt.ylim(Y_MIN, Y_MAX)

plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)
plt.title(TITLE)

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
