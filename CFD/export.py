import csv
from .constants import DataMetric

def export_data(data: dict[DataMetric, list], path):
    # Convert from np.float64 to float
    for k, v in data.items():
        data[k] = list(map(float, v))

    # Zip data by frame
    # Each frame will be a row in csv
    data_list = list(data.values())
    data_by_frame = []

    # Add headers which are keys
    data_by_frame.append(tuple(i.value for i in data.keys()))

    for i in range(len(data_list[0])):
        data_by_frame.append(tuple(j[i] for j in data_list))
    
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        for i, row in enumerate(data_by_frame):
            writer.writerow(row)
