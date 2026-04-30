import os
import json

TAX_RATES = {
    "New York": 0.08875,
    "Kings": 0.08875,
    "Queens": 0.08875,
    "Bronx": 0.08875,
    "Richmond": 0.08875,
    "Nassau": 0.08625,
    "Suffolk": 0.08625,
    "DEFAULT": 0.08
}

def get_tax_rate(county_input):
    county = (county_input or "DEFAULT").strip().title()

    aliases = {
        "Manhattan": "New York",
        "Brooklyn": "Kings",
        "Staten Island": "Richmond"
    }

    county = aliases.get(county, county)
    return TAX_RATES.get(county, TAX_RATES["DEFAULT"])


def fill_all_forms(data):
    print("DATA RECEIVED:", data)

    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    files = []

    tax_rate = get_tax_rate(data.get("county"))

    filenames = [
        "mv82_filled.txt",
        "mv912_filled.txt",
        "dtf802_filled.txt"
    ]

    for name in filenames:
        path = os.path.join(output_dir, name)

        with open(path, "w") as f:
            f.write("NY DMV FORM OUTPUT\n")
            f.write("====================\n\n")
            f.write(json.dumps(data, indent=2))
            f.write("\n\n")
            f.write(f"Computed Tax Rate: {tax_rate * 100:.3f}%\n")

        files.append(name)

    return files
