import csv
from datetime import datetime, timedelta
import math
from random import randint

# Define the input and output file paths
input_file = "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/source.csv"
output_file = "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/filtered_data_daily.csv"

# Define the PM2.5 input files
pm25_files = [
    "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/EMBASSYKATHMANDU_PM2.5_2021_YTD.csv",
    "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/EMBASSYKATHMANDU_PM2.5_2022_YTD.csv",
    "/Users/bibekg/Documents/Learning/blockchain/AQI_COL/Air-Quality-Prediction/airprediction/Data/NewData/EMBASSYKATHMANDU_PM2.5_2023_YTD.csv",
]

# Define the parameters to filter
parameters = ["DEW", "KA1", "OC1", "SLP", "TMP", "VIS", "WND", "RH", "AQI"]

# Average monthly humidity percentages
average_monthly_humidity = {
    1: 79,
    2: 71,
    3: 61,
    4: 53,
    5: 57,
    6: 73,
    7: 81,
    8: 83,
    9: 82,
    10: 79,
    11: 85,
    12: 80,
}

# Average wind speed in miles per hour
average_wind_speed_mph = {
    1: 4.3,
    2: 5.0,
    3: 5.8,
    4: 6.2,
    5: 5.8,
    6: 5.4,
    7: 5.0,
    8: 4.5,
    9: 4.1,
    10: 3.9,
    11: 3.9,
    12: 3.8,
}


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


def calculate_relative_humidity(dew_point, dry_bulb_temp, month):
    e_dew = 6.112 * math.exp((17.62 * dew_point) / (dew_point + 243.12))
    e_temp = 6.112 * math.exp((17.62 * dry_bulb_temp) / (dry_bulb_temp + 243.12))
    rh = 100 * (e_dew / e_temp)
    # Adjust RH according to the average monthly humidity
    rh_adjusted = rh * (average_monthly_humidity[month] / 100)
    return rh_adjusted


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

# Read PM2.5 CSV files and extract AQI values
for pm25_file in pm25_files:
    with open(pm25_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            date_str = row.get("Date (LT)")
            if date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d %I:%M %p").date()
                date_str = date.strftime("%Y-%m-%d")
                aqi_value = float(row["AQI"])
                if (
                    aqi_value != -999 and aqi_value != -312.33
                ):  # Ignore -999 and -312.33 values
                    if date_str in date_rows:
                        date_rows[date_str]["AQI"].append(aqi_value)

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
                for param in parameters[:-2]:  # Exclude RH and AQI for now
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
        for param in parameters[:-2]:  # Exclude RH and AQI for now
            if date_rows[date_str][param]:
                aggregated_row[param] = round(
                    sum(date_rows[date_str][param]) / len(date_rows[date_str][param]), 2
                )
            else:
                aggregated_row[param] = None

        # Calculate RH if DEW and TMP are available
        if aggregated_row["DEW"] is not None and aggregated_row["TMP"] is not None:
            month = datetime.strptime(date_str, "%Y-%m-%d").month
            aggregated_row["RH"] = round(
                calculate_relative_humidity(
                    aggregated_row["DEW"], aggregated_row["TMP"], month
                ),
                2,
            )
        else:
            aggregated_row["RH"] = None

        # Calculate the average AQI if available
        if date_rows[date_str]["AQI"]:
            aggregated_row["AQI"] = round(
                sum(date_rows[date_str]["AQI"]) / len(date_rows[date_str]["AQI"]), 2
            )
        else:
            # Use AQI from the same date in other years if available
            aqi_values = []
            for year_offset in [-1, 1]:
                other_year_date_str = (
                    datetime.strptime(date_str, "%Y-%m-%d")
                    + timedelta(days=365 * year_offset)
                ).strftime("%Y-%m-%d")
                if other_year_date_str in date_rows and isinstance(
                    date_rows[other_year_date_str]["AQI"], list
                ):
                    aqi_values.extend(date_rows[other_year_date_str]["AQI"])
            if aqi_values:
                aggregated_row["AQI"] = round(sum(aqi_values) / len(aqi_values), 2)
            else:
                aggregated_row["AQI"] = None

        # Handle missing current row attributes based on previous row data
        if previous_row:
            for param in parameters:
                if aggregated_row[param] is None:
                    aggregated_row[param] = previous_row[param]

        # Adjust wind speed and temperature
        month = datetime.strptime(date_str, "%Y-%m-%d").month
        average_wind_speed_kph = (
            average_wind_speed_mph[month] * 1.60934
        )  # Convert to km/h

        # Ensure WND is not greater than OC1
        if (
            "WND" in aggregated_row
            and "OC1" in aggregated_row
            and aggregated_row["WND"] is not None
            and aggregated_row["OC1"] is not None
        ):
            if aggregated_row["WND"] > aggregated_row["OC1"]:
                aggregated_row["WND"] = aggregated_row["OC1"]

        # Adjust wind speed to average if necessary
        if (
            "WND" in aggregated_row
            and aggregated_row["WND"] is not None
            and aggregated_row["WND"] > average_wind_speed_kph
        ):
            aggregated_row["WND"] = average_wind_speed_kph

        # Calculate average temperature
        if (
            "KA1" in aggregated_row
            and "OC1" in aggregated_row
            and aggregated_row["KA1"] is not None
            and aggregated_row["OC1"] is not None
        ):
            aggregated_row["TMP"] = round(
                (aggregated_row["KA1"] + aggregated_row["OC1"]) / 2, 2
            )

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

# Define the new headers
new_headers = {
    "DEW": "Tm",
    "KA1": "TM",
    "OC1": "VM",
    "SLP": "SLP",
    "TMP": "T",
    "VIS": "VV",
    "WND": "V",
    "RH": "H",
    "AQI": "AQI",
}

# Open the output CSV file with new headers
with open(output_file, mode="w", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["Date"] + list(new_headers.values()))
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
                        row[param] = round(
                            sum(date_rows[previous_year_date_str][param])
                            / len(date_rows[previous_year_date_str][param]),
                            2,
                        )
                    elif (
                        latest_year_date_str in date_rows
                        and date_rows[latest_year_date_str][param]
                    ):
                        row[param] = round(
                            sum(date_rows[latest_year_date_str][param])
                            / len(date_rows[latest_year_date_str][param]),
                            2,
                        )

        # Adjust wind speed and temperature
        month = datetime.strptime(row["Date"], "%Y-%m-%d").month
        average_wind_speed_kph = (
            average_wind_speed_mph[month] * 1.60934
        )  # Convert to km/h

        # Rename the headers in the row
        new_row = {new_headers.get(param, param): value for param, value in row.items()}

        # Ensure WND is not greater than OC1
        if (
            "V" in new_row
            and "VM" in new_row
            and float(new_row["V"]) > float(new_row["VM"])
        ):
            new_row["V"] = round(float(new_row["VM"]) - randint(1, 3), 2)

        # Calculate average temperature
        if (
            "TM" in new_row
            and "Tm" in new_row
            and "T" in new_row
            and float(new_row["T"])  # actual average temperature
            < round(
                (float(new_row["TM"]) + float(new_row["VM"])) / 2, 2
            )  # calculated average temperature
        ):
            new_row["T"] = round((float(new_row["TM"]) + float(new_row["VM"])) / 2, 2)
        new_row["V"] = round(float(new_row["V"]), 2)
        writer.writerow(new_row)
        previous_row = row
