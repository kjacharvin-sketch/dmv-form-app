import os
from pdfrw import PdfReader, PdfWriter

# ---------- SAFE HELPERS ----------
def safe_str(v):
    return str(v).strip() if v else ""

def safe_int(v):
    try:
        return int(str(v).replace(",", "").strip())
    except:
        return 0

def safe_float(v):
    try:
        return float(str(v).replace(",", "").strip())
    except:
        return 0.0


# ---------- TAX ----------
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


# ---------- PDF WRITE ----------
def simple_fill(input_path, output_path, text_lines):
    pdf = PdfReader(input_path)

    for page in pdf.pages:
        if not hasattr(page, "Contents"):
            continue

        content = "\n".join(text_lines)

        # crude text injection (safe fallback)
        page.Contents.stream = page.Contents.stream + f"\n% {content}"

    PdfWriter().write(output_path, pdf)


# ---------- MAIN ----------
def fill_all_forms(data):
    print("DATA RECEIVED:", data)

    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    files = []

    # clean inputs
    buyer = safe_str(data.get("buyer_name"))
    vin = safe_str(data.get("vin"))
    county = safe_str(data.get("county"))
    price = safe_int(data.get("sale_price"))

    tax_rate = get_tax_rate(county)
    tax_amount = round(price * tax_rate, 2)

    text_lines = [
        f"Buyer: {buyer}",
        f"VIN: {vin}",
        f"Price: ${price}",
        f"Tax Rate: {tax_rate * 100:.3f}%",
        f"Tax: ${tax_amount}"
    ]

    forms = [
        ("mv82.pdf", "mv82_filled.pdf"),
        ("mv912.pdf", "mv912_filled.pdf"),
        ("dtf802.pdf", "dtf802_filled.pdf"),
    ]

    for template, output in forms:
        input_path = os.path.join(os.getcwd(), "templates", template)
        output_path = os.path.join(output_dir, output)

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Missing template: {template}")

        simple_fill(input_path, output_path, text_lines)

        files.append(output)

    return files
