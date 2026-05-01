import os
from pdfrw import PdfReader, PdfWriter, PageMerge

# --- TAX RATES ---
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


def fill_pdf(input_path, output_path, text):
    pdf = PdfReader(input_path)
    for page in pdf.pages:
        merger = PageMerge(page)
        # simple text overlay (we'll refine positions later)
        merger.add(pdfrw.PdfDict(
            stream=f"BT /F1 12 Tf 100 700 Td ({text}) Tj ET"
        ))
        merger.render()
    PdfWriter().write(output_path, pdf)


def fill_all_forms(data):
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    tax_rate = get_tax_rate(data.get("county"))

    files = []

    forms = [
        ("mv82.pdf", "mv82_filled.pdf"),
        ("mv912.pdf", "mv912_filled.pdf"),
        ("dtf802.pdf", "dtf802_filled.pdf"),
    ]

    for template, output in forms:
        input_path = os.path.join(os.getcwd(), "templates", template)
        output_path = os.path.join(output_dir, output)

        text = f"{data.get('buyer_name','')} | VIN: {data.get('vin','')} | TAX: {tax_rate*100:.2f}%"

        fill_pdf(input_path, output_path, text)

        files.append(output)

    return files
