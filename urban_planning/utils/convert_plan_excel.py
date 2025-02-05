import pandas as pd
import json

# Path to the input JSON file
input_json_file = "/data/jd_data/CityGen-LLM-Planning/planning/user_input_test_12_08/plan_iteration_0.json"  # Replace with your JSON file path
output_excel_file = "/data/jd_data/CityGen-LLM-Planning/planning/user_input_test_12_08/plan_iteration_0.xlsx"

# Read the JSON file
with open(input_json_file, "r") as file:
    data = json.load(file)

# Convert JSON data to a pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')

# Save the DataFrame to an Excel file
df.to_excel(output_excel_file, index=False)

print(f"Data has been successfully written to {output_excel_file}")
