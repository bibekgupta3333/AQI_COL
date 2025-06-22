import csv
from datetime import datetime, timedelta

# Define the input and output file paths
input_file = "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/source.csv"
output_file = "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/filtered_data_daily.csv"

# Define the parameters to filter
parameters = ["DEW", "KA1", "OC1", "SLP", "TMP", "VIS", "WND"]


# Conversion functions
def convert_dew_point(value):
    return int(value[:4]) / 10.0


def convert_extreme_air_temp(value):
    return int(value.split(",")[2]) / 10.0


def convert_wind_gust(value):
    return int(value.split(",")[0]) / 10.0


def convert_sea_level_pressure(value):
    return int(value.split(",")[0]) / 10.0


def convert_dry_bulb_temp(value):
    return int(value[:4]) / 10.0


def convert_visibility(value):
    return int(value[:6]) / 1000.0


def convert_wind_observation(value):
    return int(value.split(",")[0]) / 10.0


# Initialize the dictionary for all days in the range from 2021 to 2023
date_rows = {}
start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)
current_date = start_date

while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    date_rows[date_str] = {param: [] for param in parameters}
    date_rows[date_str]["Date"] = date_str
    current_date += timedelta(days=1)

# Open the input CSV file
with open(input_file, mode="r") as infile:
    reader = csv.DictReader(infile)

    # Process each row in the input file
    for row in reader:
        # Extract the date and convert it to a datetime object
        date_str = row.get("DATE")
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()
            date_str = date.strftime("%Y-%m-%d")

            # Update the dictionary with non-missing values
            if date_str in date_rows:
                for param in parameters:
                    if row.get(param):
                        try:
                            if param == "DEW":
                                date_rows[date_str][param].append(
                                    convert_dew_point(row[param])
                                )
                            elif param == "KA1":
                                date_rows[date_str][param].append(
                                    convert_extreme_air_temp(row[param])
                                )
                            elif param == "OC1":
                                date_rows[date_str][param].append(
                                    convert_wind_gust(row[param])
                                )
                            elif param == "SLP":
                                date_rows[date_str][param].append(
                                    convert_sea_level_pressure(row[param])
                                )
                            elif param == "TMP":
                                date_rows[date_str][param].append(
                                    convert_dry_bulb_temp(row[param])
                                )
                            elif param == "VIS":
                                date_rows[date_str][param].append(
                                    convert_visibility(row[param])
                                )
                            elif param == "WND":
                                date_rows[date_str][param].append(
                                    convert_wind_observation(row[param])
                                )
                        except ValueError:
                            # Skip invalid data
                            continue

# Open the output CSV file
with open(output_file, mode="w", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["Date"] + parameters)
    writer.writeheader()

    # Write the aggregated rows to the output file
    previous_row = None
    for date_str, aggregated_row in date_rows.items():
        # Calculate the average for each parameter if there are values
        for param in parameters:
            if date_rows[date_str][param]:
                aggregated_row[param] = sum(date_rows[date_str][param]) / len(
                    date_rows[date_str][param]
                )
            else:
                aggregated_row[param] = None

        # Handle missing current row attributes based on previous row data
        if previous_row:
            for param in parameters:
                if aggregated_row[param] is None:
                    aggregated_row[param] = previous_row[param]

        # Write the row to the output file
        writer.writerow(aggregated_row)
        previous_row = aggregated_row

# Re-read the filtered data and fill in any remaining missing values
with open(output_file, mode="r") as infile:
    reader = list(csv.DictReader(infile))

# Reinitialize date_rows to store lists of values for filling missing data
date_rows = {row["Date"]: {param: [] for param in parameters} for row in reader}
for row in reader:
    for param in parameters:
        if row[param] != "":
            date_rows[row["Date"]][param].append(float(row[param]))

with open(output_file, mode="w", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["Date"] + parameters)
    writer.writeheader()

    previous_row = None
    for row in reader:
        for param in parameters:
            if row[param] == "" or row[param] is None:
                if previous_row and previous_row[param] != "":
                    row[param] = previous_row[param]
                else:
                    # Use the same data from the previous year or latest year date
                    date_str = row["Date"]
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    previous_year_date_str = (date - timedelta(days=365)).strftime(
                        "%Y-%m-%d"
                    )
                    latest_year_date_str = (date + timedelta(days=365)).strftime(
                        "%Y-%m-%d"
                    )
                    if (
                        previous_year_date_str in date_rows
                        and date_rows[previous_year_date_str][param]
                    ):
                        row[param] = sum(
                            date_rows[previous_year_date_str][param]
                        ) / len(date_rows[previous_year_date_str][param])
                    elif (
                        latest_year_date_str in date_rows
                        and date_rows[latest_year_date_str][param]
                    ):
                        row[param] = sum(date_rows[latest_year_date_str][param]) / len(
                            date_rows[latest_year_date_str][param]
                        )
        writer.writerow(row)
        previous_row = row
