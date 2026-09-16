"""
Universal Multi-Manufacturer Vehicle Profiles & VIN Decoders
Supports: Chevy, GMC, Ford, Toyota, Lexus, Honda, Mazda, VW, Hyundai, Kia, Nissan
"""

WMI_DATABASE = {
    # General Motors (Chevy, GMC, Cadillac, Buick)
    "1G1": ("Chevrolet", "USA", "Passenger Car"),
    "1GC": ("Chevrolet", "USA", "Truck"),
    "1GN": ("Chevrolet", "USA", "SUV / MPV"),
    "1GT": ("GMC", "USA", "Truck / SUV"),
    "2G1": ("Chevrolet", "Canada", "Passenger Car"),
    "2GN": ("Chevrolet", "Canada", "SUV / MPV"),
    "2GT": ("GMC", "Canada", "Truck / SUV"),
    "3GC": ("Chevrolet", "Mexico", "Truck"),
    "3GT": ("GMC", "Mexico", "Truck"),
    
    # Ford / Lincoln
    "1FA": ("Ford", "USA", "Passenger Car"),
    "1FB": ("Ford", "USA", "Bus / Commercial"),
    "1FC": ("Ford", "USA", "Chassis Cab"),
    "1FD": ("Ford", "USA", "Incomplete Vehicle"),
    "1FM": ("Ford", "USA", "SUV / Crossover"),
    "1FT": ("Ford", "USA", "Truck"),
    "2FA": ("Ford", "Canada", "Passenger Car"),
    "2FM": ("Ford", "Canada", "SUV"),
    "2FT": ("Ford", "Canada", "Truck"),
    "3FA": ("Ford", "Mexico", "Passenger Car"),
    "3FM": ("Ford", "Mexico", "SUV"),
    "3FT": ("Ford", "Mexico", "Truck"),
    
    # Toyota / Lexus
    "JT": ("Toyota", "Japan", "Passenger / SUV"),
    "JTH": ("Lexus", "Japan", "Passenger Car"),
    "JTJ": ("Lexus", "Japan", "SUV"),
    "2T1": ("Toyota", "Canada", "Passenger Car"),
    "2T2": ("Lexus", "Canada", "SUV"),
    "4T1": ("Toyota", "USA", "Passenger Car"),
    "5TB": ("Toyota", "USA", "Truck"),
    "5TD": ("Toyota", "USA", "SUV"),
    "5TF": ("Toyota", "USA", "Truck"),

    # Honda / Acura
    "1HG": ("Honda", "USA", "Passenger Car"),
    "2HG": ("Honda", "Canada", "Passenger Car"),
    "2HK": ("Honda", "Canada", "SUV / MPV"),
    "5J6": ("Honda", "USA", "SUV"),
    "5J8": ("Acura", "USA", "SUV"),
    "JHM": ("Honda", "Japan", "Passenger Car"),
    "JH4": ("Acura", "Japan", "Passenger Car"),
    "7FA": ("Honda", "USA", "Truck / Ridgeline"),

    # Mazda
    "JM1": ("Mazda", "Japan", "Passenger Car"),
    "JM3": ("Mazda", "Japan", "SUV"),
    "3MZ": ("Mazda", "Mexico", "Passenger Car"),
    "4F4": ("Mazda", "USA", "Truck / SUV"),

    # Hyundai / Kia
    "KM8": ("Hyundai", "Korea", "SUV"),
    "KMH": ("Hyundai", "Korea", "Passenger Car"),
    "5NP": ("Hyundai", "USA", "Passenger / SUV"),
    "KNA": ("Kia", "Korea", "Passenger Car"),
    "KND": ("Kia", "Korea", "SUV / MPV"),
    "5XX": ("Kia", "USA", "Passenger Car"),
    "5XY": ("Kia", "USA", "SUV"),

    # Nissan / Infiniti
    "1N4": ("Nissan", "USA", "Passenger Car"),
    "1N6": ("Nissan", "USA", "Truck"),
    "5N1": ("Nissan", "USA", "SUV"),
    "JN1": ("Nissan", "Japan", "Passenger Car"),
    "JN8": ("Nissan", "Japan", "SUV"),
    "JNK": ("Infiniti", "Japan", "Passenger Car"),
    "JNR": ("Infiniti", "Japan", "SUV"),

    # Volkswagen / Audi
    "1VW": ("Volkswagen", "USA", "Passenger Car"),
    "3VW": ("Volkswagen", "Mexico", "Passenger Car"),
    "WVW": ("Volkswagen", "Germany", "Passenger Car"),
    "WAU": ("Audi", "Germany", "Passenger Car"),
    "WA1": ("Audi", "Germany", "SUV")
}

YEAR_CODES = {
    'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015,
    'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
    'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025, 'T': 2026
}

MANUFACTURER_PROFILES = {
    "Chevrolet": {
        "group": "General Motors",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "Transmission Fluid Temp", "service": 0x22, "did": 0x1940, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Engine Oil Life Remaining", "service": 0x22, "did": 0x11A0, "unit": "%", "calc": "A"},
            {"name": "Ethanol / Alcohol Fuel Content", "service": 0x01, "pid": 0x52, "unit": "%", "calc": "(A * 100) / 255"}
        ]
    },
    "GMC": {
        "group": "General Motors",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "Transmission Fluid Temp", "service": 0x22, "did": 0x1940, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Engine Oil Life Remaining", "service": 0x22, "did": 0x11A0, "unit": "%", "calc": "A"}
        ]
    },
    "Ford": {
        "group": "Ford Motor Co.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "Cylinder Head Temp (CHT)", "service": 0x22, "did": 0xF405, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Transmission Fluid Temp (TFT)", "service": 0x22, "did": 0x1E1C, "unit": "°F", "calc": "((((A*256)+B)/16.0 - 40)*9/5)+32"},
            {"name": "Fuel Rail Pressure (High)", "service": 0x01, "pid": 0x23, "unit": "PSI", "calc": "((A * 256) + B) * 1.45"}
        ]
    },
    "Toyota": {
        "group": "Toyota Motor Corp.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E2, "tcm_resp": 0x7EA,
        "enhanced_pids": [
            {"name": "Automatic Transmission Fluid Temp (Pan)", "service": 0x21, "did": 0xD9, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "AT Fluid Temp (Torque Converter)", "service": 0x21, "did": 0xD9, "unit": "°F", "calc": "((B - 40) * 9/5) + 32"},
            {"name": "Hybrid Battery State of Charge (SOC)", "service": 0x01, "pid": 0x5B, "unit": "%", "calc": "(A * 100) / 255"}
        ]
    },
    "Lexus": {
        "group": "Toyota Motor Corp.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E2, "tcm_resp": 0x7EA,
        "enhanced_pids": [
            {"name": "A/T Oil Temp (Pan)", "service": 0x21, "did": 0xD9, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Hybrid Inverter Temp", "service": 0x21, "did": 0xCE, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"}
        ]
    },
    "Honda": {
        "group": "Honda Motor Co.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "CVT / AT Fluid Temp", "service": 0x22, "did": 0x2201, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Engine Oil Life Remaining", "service": 0x22, "did": 0x2220, "unit": "%", "calc": "A"}
        ]
    },
    "Mazda": {
        "group": "Mazda Motor Corp.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "Transmission Fluid Temp", "service": 0x22, "did": 0x1E1C, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "SkyActiv Cylinder Head Temp", "service": 0x22, "did": 0xF405, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"}
        ]
    },
    "Hyundai": {
        "group": "Hyundai Motor Group",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E2, "tcm_resp": 0x7EA,
        "enhanced_pids": [
            {"name": "Automatic / DCT Transmission Temp", "service": 0x21, "did": 0x02, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Turbo Boost Pressure", "service": 0x01, "pid": 0x0B, "unit": "PSI", "calc": "A * 0.145 - 14.7"}
        ]
    },
    "Kia": {
        "group": "Hyundai Motor Group",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E2, "tcm_resp": 0x7EA,
        "enhanced_pids": [
            {"name": "Automatic / DCT Transmission Temp", "service": 0x21, "did": 0x02, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"}
        ]
    },
    "Nissan": {
        "group": "Nissan Motor Co.",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "CVT Fluid Deterioration Date (Score)", "service": 0x21, "did": 0x01, "unit": "Pts", "calc": "(A * 256) + B"},
            {"name": "CVT Fluid Temperature", "service": 0x21, "did": 0x01, "unit": "°F", "calc": "((C - 40) * 9/5) + 32"}
        ]
    },
    "Volkswagen": {
        "group": "Volkswagen AG",
        "hs_can_speed": 500000,
        "ecm_req": 0x7E0, "ecm_resp": 0x7E8,
        "tcm_req": 0x7E1, "tcm_resp": 0x7E9,
        "enhanced_pids": [
            {"name": "DSG / Transmission Fluid Temp", "service": 0x22, "did": 0x022F, "unit": "°F", "calc": "((A - 40) * 9/5) + 32"},
            {"name": "Engine Oil Level", "service": 0x22, "did": 0x02F0, "unit": "mm", "calc": "A"}
        ]
    }
}

def decode_vin_details(vin: str) -> dict:
    vin = vin.strip().upper()
    if len(vin) < 11:
        return {
            "vin": vin,
            "make": "Universal OBD-II Vehicle",
            "country": "Unknown",
            "type": "Passenger Vehicle",
            "year": 2019,
            "profile": MANUFACTURER_PROFILES["Chevrolet"]
        }

    # WMI (Digits 1-3)
    wmi_3 = vin[:3]
    wmi_2 = vin[:2]
    
    make = "Universal"
    country = "Global"
    vtype = "Vehicle"

    if wmi_3 in WMI_DATABASE:
        make, country, vtype = WMI_DATABASE[wmi_3]
    elif wmi_2 in WMI_DATABASE:
        make, country, vtype = WMI_DATABASE[wmi_2]

    # Year (Digit 10)
    year_char = vin[9] if len(vin) >= 10 else 'K'
    year = YEAR_CODES.get(year_char, 2019)

    profile = MANUFACTURER_PROFILES.get(make, MANUFACTURER_PROFILES["Chevrolet"])

    return {
        "vin": vin,
        "make": make,
        "country": country,
        "type": vtype,
        "year": year,
        "model_string": f"{year} {make} ({vtype})",
        "profile": profile
    }
