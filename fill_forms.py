#!/usr/bin/env python3
"""Fill NY DMV forms: DTF-802, MV-82, MV-912 from a JSON data payload."""

import json
import sys
import os
import subprocess
import tempfile
from pathlib import Path

import os
SKILL_DIR = os.getcwd()

def run_fill_script(input_pdf, fields_json_path, output_pdf):
    cmd = [
        "python", f"{SKILL_DIR}/scripts/fill_pdf_form_with_annotations.py",
        input_pdf, fields_json_path, output_pdf
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Fill script failed: {result.stderr}")
    return result.stdout

def run_fill_fillable(input_pdf, field_values_path, output_pdf):
    cmd = [
        "python", f"{SKILL_DIR}/scripts/fill_fillable_fields.py",
        input_pdf, field_values_path, output_pdf
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Fill script failed: {result.stderr}")
    return result.stdout


def fill_mv912(data, input_pdf, output_pdf):
    """Fill MV-912 Vehicle Bill of Sale (fillable PDF)."""
    fields = [
        {"field_id": "Seller", "description": "Seller name", "page": 1,
         "value": data.get("seller_name", "")},
        {"field_id": "Consideration", "description": "Sale price", "page": 1,
         "value": data.get("sale_price", "")},
        {"field_id": "Buyer", "description": "Buyer name", "page": 1,
         "value": data.get("buyer_name", "")},
        {"field_id": "Year", "description": "Vehicle year", "page": 1,
         "value": data.get("vehicle_year", "")},
        {"field_id": "Make", "description": "Vehicle make", "page": 1,
         "value": data.get("vehicle_make", "")},
        {"field_id": "Model", "description": "Vehicle model", "page": 1,
         "value": data.get("vehicle_model", "")},
        {"field_id": "Vehicle or Hull Identification Number", "description": "VIN", "page": 1,
         "value": data.get("vin", "")},
        {"field_id": "Name Seller", "description": "Seller printed name", "page": 1,
         "value": data.get("seller_name", "")},
        {"field_id": "Address Seller", "description": "Seller address", "page": 1,
         "value": data.get("seller_address", "")},
        {"field_id": "Date Seller Signature", "description": "Date seller signed", "page": 1,
         "value": data.get("transaction_date", "")},
        {"field_id": "Name Buyer", "description": "Buyer printed name", "page": 1,
         "value": data.get("buyer_name", "")},
        {"field_id": "Address Buyer", "description": "Buyer address", "page": 1,
         "value": data.get("buyer_address", "")},
        {"field_id": "Date Buyer Signature", "description": "Date buyer signed", "page": 1,
         "value": data.get("transaction_date", "")},
    ]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(fields, f)
        tmp = f.name
    try:
        run_fill_fillable(input_pdf, tmp, output_pdf)
    finally:
        os.unlink(tmp)


def fill_mv82(data, input_pdf, output_pdf):
    """Fill MV-82 Vehicle Registration/Title Application (fillable PDF)."""
    fields = []

    def add(field_id, value, page=1):
        if value:
            fields.append({"field_id": field_id, "description": field_id, "page": page, "value": value})

    # Section 1 - Registrant
    add("NYS New York State driver license ID Identification number of PRIMARY REGISTRANT", data.get("registrant_license", ""))
    
    buyer_name = data.get("buyer_name", "")
    add("VEHICLE IDENTIFICATION NUMBER", data.get("vin", ""))
    add("VEHICLE DESCRIPTION Year", data.get("vehicle_year", ""))
    add("VEHICLE DESCRIPTION Make", data.get("vehicle_make", ""))
    add("Color", data.get("vehicle_color", ""))
    add("Odometer Reading in Miles", data.get("odometer", ""))

    # Mailing address
    buyer_addr = data.get("buyer_address", "")
    buyer_city = data.get("buyer_city", "")
    buyer_state = data.get("buyer_state", "NY")
    buyer_zip = data.get("buyer_zip", "")
    buyer_county = data.get("buyer_county", "")

    add("THE ADDRESS WHERE PRIMARY REGISTRANT GETS MAIL", buyer_addr)
    add("THE ADDRESS WHERE PRIMARY REGISTRANT GETS MAIL City or Town", buyer_city)
    add("THE ADDRESS WHERE PRIMARY REGISTRANT GETS MAIL Zip Code", buyer_zip)
    add("County of Residence", buyer_county)

    # DOB
    add("PRIMARY REGISTRANT DATE OF BIRTH Year", data.get("registrant_dob_year", ""))

    # Phone
    add("PRIMARY REGISTRANT TELEPHONE or MOBILE PHONE NUMBER Area Code", data.get("registrant_phone_area", ""))
    add("PRIMARY REGISTRANT TELEPHONE or MOBILE PHONE NUMBER", data.get("registrant_phone", ""))

    # Section 3 - Owner (if different, but often same)
    add("NAME OF PRIMARY OWNER Last First Middle", data.get("buyer_name", ""))
    add("THE ADDRESS WHERE PRIMARY OWNER GETS MAIL", buyer_addr)
    add("THE ADDRESS WHERE PRIMARY OWNER GETS MAIL City or Town", buyer_city)
    add("THE ADDRESS WHERE PRIMARY OWNER GETS MAIL Zip Code", buyer_zip)
    add("THE ADDRESS WHERE PRIMARY OWNER GETS MAIL County", buyer_county)

    # Damage disclosure - No
    fields.append({"field_id": "Has the vehicle been wrecked destroyed or damaged to such an extent that the total estimate or actual cost of parts and labor to rebuild or reconstruct the vehicle to the condition it was in before an accident and to make the vehicle legal to operate on the road or highways is more than 75 of the retail value of the vehicle at the time of loss",
                   "description": "Damage disclosure", "page": 2, "value": "/No"})
    fields.append({"field_id": "Has this vehicle been modified from the original manufacturer specifications without extending the chassis or lengthening the wheel base",
                   "description": "Modifications", "page": 2, "value": "/No"})

    # Certification name
    add("Print Name Here", data.get("buyer_name", ""), page=2)

    # Personal use
    fields.append({"field_id": "A Is this vehicle being registered only for personal use",
                   "description": "Personal use", "page": 1, "value": "/Yes"})

    # I want to: Register a vehicle
    fields.append({"field_id": "I WANT TO",
                   "description": "Action", "page": 1, "value": "/REGISTER A VEHICLE"})

    # Body type
    body = data.get("body_type", "4-Door")
    body_map = {
        "2-Door": "/2-Door", "4-Door": "/4-Door", "Pick-up": "/Pick-up",
        "Van": "/Van", "SUV": "/Suburban/SUV", "Motorcycle": "/Motorcycle",
        "Trailer": "/Trailer", "Convertible": "/Convertible"
    }
    fields.append({"field_id": "Body Type", "description": "Body type", "page": 1,
                   "value": body_map.get(body, "/4-Door")})

    # Fuel type
    fuel = data.get("fuel_type", "Gas")
    fuel_map = {
        "Gas": "/Gas", "Diesel": "/Diesel", "Electric": "/Electric",
        "Flex": "/Flex", "CNG": "/CNG", "Propane": "/Propane", "None": "/None"
    }
    fields.append({"field_id": "Type of Power Fuel", "description": "Fuel", "page": 1,
                   "value": fuel_map.get(fuel, "/Gas")})

    # Limousine: No
    fields.append({"field_id": "Is this vehicle a limousine stretch limousine or otherwise altered to increase seating capacity",
                   "description": "Limousine", "page": 1, "value": "/No"})

    # Registrant sex
    sex = data.get("registrant_sex", "M")
    sex_map = {"M": "/M (Male)", "F": "/F (Female)", "X": "/X (indeterminate/unspecified) "}
    fields.append({"field_id": "PRIMARY REGISTRANT SEX", "description": "Sex", "page": 1,
                   "value": sex_map.get(sex, "/M (Male)")})

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(fields, f)
        tmp = f.name
    try:
        run_fill_fillable(input_pdf, tmp, output_pdf)
    finally:
        os.unlink(tmp)


def fill_dtf802(data, input_pdf, output_pdf):
    """Fill DTF-802 Statement of Transaction (non-fillable, annotation-based)."""
    # PDF is 612x792. y=0 at TOP in annotation coords.
    # From visual analysis of page images (772x1000 px):
    # pdf_x = img_x * 612/772; pdf_y = img_y * 792/1000

    def sc(ix, iy):
        """Scale image coords to PDF coords."""
        return [ix * 612 / 772, iy * 792 / 1000]

    vehicle_year = data.get("vehicle_year", "")
    vehicle_make = data.get("vehicle_make", "")
    vehicle_model = data.get("vehicle_model", "")
    vin = data.get("vin", "")
    buyer_name = data.get("buyer_name", "")
    buyer_ssn = data.get("buyer_ssn", "")
    buyer_addr = data.get("buyer_address", "")
    buyer_city_state_zip = f"{data.get('buyer_city','')}, {data.get('buyer_state','NY')} {data.get('buyer_zip','')}"
    buyer_county = data.get("buyer_county", "")
    seller_name = data.get("seller_name", "")
    seller_addr = data.get("seller_address", "")
    seller_city_state_zip = f"{data.get('seller_city','')}, {data.get('seller_state','NY')} {data.get('seller_zip','')}"
    seller_county = data.get("seller_county", "")
    txn_date = data.get("transaction_date", "")
    sale_price = data.get("sale_price", "")
    relationship = data.get("relationship", "None")

    fields_p1 = {
        "pdf_width": 612,
        "pdf_height": 792
    }

    form_fields = []

    # --- Section 1: Vehicle type checkbox - exact coords from structure ---
    vtype = data.get("vehicle_type", "Motor vehicle")
    type_positions = {
        "Motor vehicle":         [29.2, 288.5, 40.8, 299.0],
        "Trailer":               [124.2, 288.5, 135.8, 299.0],
        "Boat/Trailer combination": [187.2, 288.5, 198.8, 299.0],
        "ATV":                   [308.0, 288.5, 319.5, 299.0],
        "Snowmobile":            [372.2, 288.5, 383.8, 299.0],
        "Boat":                  [456.5, 288.5, 468.0, 299.0],
    }
    if vtype in type_positions:
        box = type_positions[vtype]
        form_fields.append({
            "page_number": 1,
            "description": f"Vehicle type: {vtype}",
            "field_label": vtype,
            "label_bounding_box": [box[0]+15, box[1], box[0]+60, box[3]],
            "entry_bounding_box": [box[0], box[1], box[2], box[3]],
            "entry_text": {"text": "X", "font_size": 8}
        })

    # Year
    form_fields.append({
        "page_number": 1, "description": "Vehicle year",
        "field_label": "Year",
        "label_bounding_box": [27, 305, 50, 315],
        "entry_bounding_box": [27, 315, 80, 326],
        "entry_text": {"text": vehicle_year, "font_size": 9}
    })
    # Make
    form_fields.append({
        "page_number": 1, "description": "Vehicle make",
        "field_label": "Make",
        "label_bounding_box": [93, 305, 130, 315],
        "entry_bounding_box": [93, 315, 230, 326],
        "entry_text": {"text": vehicle_make, "font_size": 9}
    })
    # Model
    form_fields.append({
        "page_number": 1, "description": "Vehicle model",
        "field_label": "Model",
        "label_bounding_box": [255, 305, 300, 315],
        "entry_bounding_box": [255, 315, 395, 326],
        "entry_text": {"text": vehicle_model, "font_size": 9}
    })
    # VIN
    form_fields.append({
        "page_number": 1, "description": "VIN",
        "field_label": "VIN",
        "label_bounding_box": [417, 305, 540, 315],
        "entry_bounding_box": [417, 315, 590, 326],
        "entry_text": {"text": vin, "font_size": 8}
    })

    # --- Section 2: New owner ---
    form_fields.append({
        "page_number": 1, "description": "New owner name",
        "field_label": "New owner name",
        "label_bounding_box": [27, 434, 200, 444],
        "entry_bounding_box": [27, 444, 430, 455],
        "entry_text": {"text": buyer_name, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "New owner SSN/TIN/EIN",
        "field_label": "SSN/TIN/EIN",
        "label_bounding_box": [453, 434, 590, 444],
        "entry_bounding_box": [453, 444, 590, 455],
        "entry_text": {"text": buyer_ssn, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "New owner address",
        "field_label": "Address",
        "label_bounding_box": [27, 457, 200, 467],
        "entry_bounding_box": [27, 467, 290, 478],
        "entry_text": {"text": buyer_addr, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "New owner city state zip",
        "field_label": "City/State/ZIP",
        "label_bounding_box": [290, 457, 430, 467],
        "entry_bounding_box": [290, 467, 430, 478],
        "entry_text": {"text": buyer_city_state_zip, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "New owner county",
        "field_label": "County",
        "label_bounding_box": [430, 457, 590, 467],
        "entry_bounding_box": [430, 467, 590, 478],
        "entry_text": {"text": buyer_county, "font_size": 9}
    })

    # --- Section 3: Previous owner ---
    form_fields.append({
        "page_number": 1, "description": "Previous owner name",
        "field_label": "Prev owner name",
        "label_bounding_box": [27, 530, 400, 540],
        "entry_bounding_box": [27, 540, 430, 551],
        "entry_text": {"text": seller_name, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "Previous owner address",
        "field_label": "Prev addr",
        "label_bounding_box": [27, 553, 200, 563],
        "entry_bounding_box": [27, 563, 290, 574],
        "entry_text": {"text": seller_addr, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "Previous owner city state zip",
        "field_label": "Prev city/state/zip",
        "label_bounding_box": [290, 553, 430, 563],
        "entry_bounding_box": [290, 563, 430, 574],
        "entry_text": {"text": seller_city_state_zip, "font_size": 9}
    })
    form_fields.append({
        "page_number": 1, "description": "Previous owner county",
        "field_label": "Prev county",
        "label_bounding_box": [430, 553, 590, 563],
        "entry_bounding_box": [430, 563, 590, 574],
        "entry_text": {"text": seller_county, "font_size": 9}
    })

    # --- Section 4: Transaction info ---
    # Date
    if txn_date:
        form_fields.append({
            "page_number": 1, "description": "Transaction date",
            "field_label": "Date",
            "label_bounding_box": [27, 595, 110, 605],
            "entry_bounding_box": [27, 605, 110, 616],
            "entry_text": {"text": txn_date, "font_size": 9}
        })

    # Relationship checkbox - exact coords from structure
    rel_positions = {
        "None":       [124.2, 613.2, 135.8, 623.8],
        "Spouse":     [172.2, 613.2, 183.8, 623.8],
        "Parent":     [228.2, 613.2, 239.8, 623.8],
        "Child":      [282.2, 613.2, 293.8, 623.8],
        "Stepparent": [331.2, 613.2, 342.8, 623.8],
        "Stepchild":  [398.2, 613.2, 409.8, 623.8],
        "Other":      [460.2, 613.2, 471.8, 623.8],
    }
    if relationship in rel_positions:
        box = rel_positions[relationship]
        form_fields.append({
            "page_number": 1, "description": f"Relationship: {relationship}",
            "field_label": relationship,
            "label_bounding_box": [box[0]+15, box[1], box[0]+50, box[3]],
            "entry_bounding_box": [box[0], box[1], box[2], box[3]],
            "entry_text": {"text": "X", "font_size": 8}
        })

    # Transaction type checkbox - using exact coords from structure
    txn_type = data.get("transaction_type", "None of the above")
    txn_type_positions = {
        "Gift to non-family": [27.2, 637.2, 38.8, 647.8],
        "Purchase below FMV non-family": [27.2, 649.2, 38.8, 659.8],
        "Gift of trailer/ATV/boat/snowmobile": [27.2, 661.2, 38.8, 671.8],
        "Purchase below FMV trailer/ATV/boat/snowmobile": [27.2, 673.2, 38.8, 683.8],
        "Gift or purchase to spouse/parent/child/stepparent/stepchild": [27.2, 685.2, 38.8, 695.8],
        "None of the above": [27.2, 697.2, 38.8, 707.8],
    }
    if txn_type in txn_type_positions:
        box = txn_type_positions[txn_type]
        form_fields.append({
            "page_number": 1, "description": f"Transaction type: {txn_type}",
            "field_label": txn_type,
            "label_bounding_box": [box[0]+15, box[1], box[0]+300, box[3]],
            "entry_bounding_box": [box[0], box[1], box[2], box[3]],
            "entry_text": {"text": "X", "font_size": 8}
        })

    # --- Page 2: Section 5 Purchase info ---
    form_fields.append({
        "page_number": 2, "description": "Cash payment amount",
        "field_label": "1a",
        "label_bounding_box": [450, 95, 520, 105],
        "entry_bounding_box": [520, 95, 590, 106],
        "entry_text": {"text": sale_price, "font_size": 9}
    })
    form_fields.append({
        "page_number": 2, "description": "Purchase price total",
        "field_label": "1d",
        "label_bounding_box": [450, 133, 520, 143],
        "entry_bounding_box": [520, 133, 590, 144],
        "entry_text": {"text": sale_price, "font_size": 9}
    })

    # Was this from spouse/parent/child?
    family_sale = data.get("family_transaction", False)
    family_x = 385 if family_sale else 483
    form_fields.append({
        "page_number": 2, "description": "Family transaction yes/no",
        "field_label": "family",
        "label_bounding_box": [family_x, 158, family_x+40, 168],
        "entry_bounding_box": [family_x-12, 159, family_x-2, 169],
        "entry_text": {"text": "X", "font_size": 8}
    })

    # Tax rate
    # County → tax rate mapping
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

# Get county


def fill_all_forms(data):
    form_fields = []   #

    county = data.get("county", "DEFAULT").strip().title()

    aliases = {
        "Manhattan": "New York",
        "Brooklyn": "Kings",
        "Staten Island": "Richmond"
    }

    county = aliases.get(county, county)

    tax_rate = TAX_RATES.get(county, TAX_RATES["DEFAULT"])

    # then your form_fields.append(...) stuff

# Write to PDF
    form_fields.append({
    "page_number": 2,
    "description": "Tax rate",
    "field_label": "Tax rate",
    "label_bounding_box": [27, 175, 200, 185],
    "entry_bounding_box": [453, 175, 520, 186],
    "entry_text": {"text": f"{tax_rate * 100:.3f}%", "font_size": 9}
})

# Section 6 if needed
if data.get("section6_needed", False):
    cash = data.get("sale_price", "")

    form_fields.append({
        "page_number": 2,
        "description": "Section 6 cash payment",
        "field_label": "6",
        "label_bounding_box": [27, 475, 450, 485],
        "entry_bounding_box": [520, 475, 590, 486],
        "entry_text": {"text": cash, "font_size": 9}
    })

    form_fields.append({
        "page_number": 2,
        "description": "Section 6 total selling price",
        "field_label": "7d",
        "label_bounding_box": [27, 575, 450, 585],
        "entry_bounding_box": [520, 575, 590, 586],
        "entry_text": {"text": cash, "font_size": 9}
    })

    seller_name_print = data.get("seller_name", "")

    form_fields.append({
        "page_number": 2,
        "description": "Seller/donor printed name",
        "field_label": "Seller name",
        "label_bounding_box": [300, 655, 500, 665],
        "entry_bounding_box": [300, 665, 500, 676],
        "entry_text": {"text": seller_name_print, "font_size": 9}
    })

    fields_doc = {
        "pages": [
            {"page_number": 1, "pdf_width": 612, "pdf_height": 792},
            {"page_number": 2, "pdf_width": 612, "pdf_height": 792}
        ],
        "form_fields": form_fields
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(fields_doc, f)
        tmp = f.name
    try:
        run_fill_script(input_pdf, tmp, output_pdf)
    finally:
        os.unlink(tmp)


def fill_all_forms(data, base_dir="/home/claude", output_dir="/mnt/user-data/outputs"):
    """Fill all three forms and return output paths."""
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    # MV-912
    try:
        out = os.path.join(output_dir, "mv912_filled.pdf")
        fill_mv912(data, os.path.join(base_dir, "mv912.pdf"), out)
        results["mv912"] = {"status": "ok", "path": out}
    except Exception as e:
        results["mv912"] = {"status": "error", "error": str(e)}

    # MV-82
    try:
        out = os.path.join(output_dir, "mv82_filled.pdf")
        fill_mv82(data, os.path.join(base_dir, "mv82.pdf"), out)
        results["mv82"] = {"status": "ok", "path": out}
    except Exception as e:
        results["mv82"] = {"status": "error", "error": str(e)}

    # DTF-802
    try:
        out = os.path.join(output_dir, "dtf802_filled.pdf")
        fill_dtf802(data, os.path.join(base_dir, "dtf802.pdf"), out)
        results["dtf802"] = {"status": "ok", "path": out}
    except Exception as e:
        results["dtf802"] = {"status": "error", "error": str(e)}

    return results

import os

def fill_all_forms(data):
    print("DATA RECEIVED:", data)

    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    files = []

    # Create test files to confirm everything works
    filenames = ["mv82_filled.txt", "mv912_filled.txt", "dtf802_filled.txt"]

    for name in filenames:
        path = os.path.join(output_dir, name)

        with open(path, "w") as f:
            f.write("THIS IS A TEST FILE\n")
            f.write(str(data))

        files.append(path)

    return files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fill_forms.py <data.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    results = fill_all_forms(data)
    print(json.dumps(results, indent=2))
