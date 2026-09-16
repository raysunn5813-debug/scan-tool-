"""
OBD-II Diagnostic Trouble Code (DTC) Database with Plain-English Explanations
"""

DTC_DB = {
    # Powertrain - Air & Fuel Metering
    "P0100": {
        "title": "Mass or Volume Air Flow Circuit Malfunction",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "The Engine Control Module (ECM) detected an abnormal signal from the MAF sensor circuit.",
        "causes": ["Dirty or contaminated MAF sensor hot-wire", "Air intake hose leaks or cracks", "Faulty MAF sensor", "Damaged wiring harness or loose connector"],
        "repair_tips": "Inspect intake duct for cracks. Clean the MAF sensor using dedicated MAF sensor cleaner spray. Check connector pins for corrosion."
    },
    "P0101": {
        "title": "Mass Air Flow (MAF) Sensor Range/Performance Problem",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "The MAF sensor reading is outside the expected operating range for the current engine speed and throttle opening.",
        "causes": ["Vacuum leak downstream of MAF", "Dirty air filter or intake blockage", "Contaminated MAF sensor", "Faulty PCV valve"],
        "repair_tips": "Check air filter condition and verify intake clamps are tight. Perform a smoke test for vacuum leaks."
    },
    "P0102": {
        "title": "Mass Air Flow (MAF) Sensor Circuit Low Frequency / Voltage",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "The MAF sensor is outputting a voltage/frequency below the minimum threshold.",
        "causes": ["Unplugged MAF connector", "Broken ground wire or 12V supply wire", "Failed MAF sensor"],
        "repair_tips": "Check 12V power and 5V reference at the MAF connector with a multimeter."
    },
    "P0103": {
        "title": "Mass Air Flow (MAF) Sensor Circuit High Frequency / Voltage",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "The MAF sensor output voltage is abnormally high.",
        "causes": ["Short to power in MAF signal line", "Internal sensor failure", "Poor ground connection"],
        "repair_tips": "Inspect wiring harness near hot engine components for pinched or melted wires."
    },
    "P0104": {
        "title": "Mass or Volume Air Flow Circuit Intermittent / Erratic",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "The MAF sensor signal is cutting in and out intermittently while driving or idling.",
        "causes": [
            "Loose or corroded MAF connector terminals",
            "Cracked air intake snorkel boot causing intermittent air bypass under engine movement",
            "Dirty hot-wire element inside MAF",
            "Chafed or intermittent wiring harness"
        ],
        "repair_tips": "1. Wiggle the MAF wiring harness while monitoring live RPM/MAF to check for dropouts.\n2. Remove MAF sensor and clean with MAF cleaner spray (never touch the wire with tools).\n3. Inspect intake bellows for hidden tears under the rubber accordions."
    },
    "P0171": {
        "title": "System Too Lean (Bank 1)",
        "system": "Fuel & Air Metering",
        "severity": "High",
        "description": "The ECM is adding maximum fuel compensation (+20% to +35% Long Term Fuel Trim) because it detects excessive unmetered oxygen.",
        "causes": ["Vacuum leak (PCV hose, intake gasket)", "Weak fuel pump or clogged fuel filter", "Faulty MAF sensor reporting lower air than actual", "Exhaust leak before upstream O2 sensor"],
        "repair_tips": "Check LTFT (Long Term Fuel Trim) live data at idle vs 2500 RPM. If trim drops at 2500 RPM, suspect a vacuum leak."
    },
    "P0172": {
        "title": "System Too Rich (Bank 1)",
        "system": "Fuel & Air Metering",
        "severity": "Moderate",
        "description": "Too much fuel or not enough air detected in combustion.",
        "causes": ["Leaking fuel injector", "High fuel pressure", "Stuck open canister purge valve (EVAP)", "Restricted air intake"],
        "repair_tips": "Check EVAP purge valve to see if it draws vacuum at idle."
    },
    "P0300": {
        "title": "Random / Multiple Cylinder Misfire Detected",
        "system": "Ignition System",
        "severity": "Critical",
        "description": "The engine is experiencing misfires across multiple cylinders, which can overheat the catalytic converter.",
        "causes": ["Worn spark plugs", "Low fuel pressure", "Intake manifold vacuum leak", "Faulty ignition coils"],
        "repair_tips": "Do not drive long distances with a blinking Check Engine Light. Inspect spark plugs and check fuel pressure."
    },
    "P0420": {
        "title": "Catalytic Converter System Efficiency Below Threshold (Bank 1)",
        "system": "Emissions Control",
        "severity": "Low to Moderate",
        "description": "The catalytic converter is not storing and burning off exhaust emissions efficiently.",
        "causes": ["Aged/degraded catalytic converter", "Exhaust leak near downstream O2 sensor", "Defective downstream oxygen sensor"],
        "repair_tips": "Verify downstream O2 sensor waveform (should be steady 0.6-0.8V, not oscillating like upstream)."
    },
    "P0442": {
        "title": "Evaporative Emission (EVAP) Control System Small Leak Detected",
        "system": "Emissions Control",
        "severity": "Low",
        "description": "The fuel tank vapor recovery system failed its vacuum decay test.",
        "causes": ["Loose or damaged gas cap seal", "Cracked EVAP vapor line", "Faulty vent solenoid valve"],
        "repair_tips": "Inspect gas cap rubber O-ring seal for dry rot or cracks and tighten until it clicks."
    },
    # Chassis Codes
    "C15AA": {
        "title": "Electronic Brake Control Module (EBCM) / Steering Angle Sensor Correlation",
        "system": "Chassis / StabiliTrak / ABS",
        "severity": "Moderate",
        "description": "GM Chassis module detected a variance between steering wheel position angle and yaw rate/lateral acceleration.",
        "causes": [
            "Recent wheel alignment without Steering Angle Sensor (SAS) reset",
            "Low battery voltage or battery disconnected recently",
            "Steering column clockspring or angle sensor calibration offset",
            "Wheel speed sensor signal glitch"
        ],
        "repair_tips": "1. Verify battery voltage is above 12.5V (low battery causes transient chassis sensor codes on GM Global-A).\n2. Turn steering wheel lock-to-lock twice while parked with engine running to recalibrate SAS.\n3. Clear code and verify if StabiliTrak light turns off."
    }
}

def lookup_dtc(code: str) -> dict:
    code = code.strip().upper()
    if code in DTC_DB:
        return DTC_DB[code]
    
    # Generic prefix decoder
    prefix = code[0] if code else "P"
    sys_type = {
        "P": "Powertrain (Engine & Transmission)",
        "C": "Chassis (ABS, Traction, Steering)",
        "B": "Body (Airbags, Climate, Lighting)",
        "U": "Network (CAN Bus & Module Communication)"
    }.get(prefix, "Automotive Subsystem")

    return {
        "title": f"Manufacturer Diagnostic Code {code}",
        "system": sys_type,
        "severity": "Moderate",
        "description": f"Vehicle diagnostic system registered diagnostic trouble code {code}.",
        "causes": ["Sensor out of calibration or circuit fault", "Intermittent electrical connector contact", "Mechanical subsystem variance"],
        "repair_tips": "Inspect wiring harness and connector pins for the associated subsystem. Clear code to verify recurrence."
    }
