"""
Nigerian state-specific tax parameters.
All states follow FIRS 2024 progressive rates (PITA).
State-specific element: Annual Development Levy (flat charge per taxpayer).
"""

STATE_DATA = {
    "Abia": {
        "irs": "Abia State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Adamawa": {
        "irs": "Adamawa State Board of Internal Revenue",
        "development_levy": 3_000,
    },
    "Akwa Ibom": {
        "irs": "Akwa Ibom State Revenue Authority",
        "development_levy": 5_000,
    },
    "Anambra": {
        "irs": "Anambra State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Bauchi": {
        "irs": "Bauchi State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Bayelsa": {
        "irs": "Bayelsa State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Benue": {
        "irs": "Benue State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Borno": {
        "irs": "Borno State Board of Internal Revenue",
        "development_levy": 3_000,
    },
    "Cross River": {
        "irs": "Cross River State Board of Internal Revenue",
        "development_levy": 5_000,
    },
    "Delta": {
        "irs": "Delta State Board of Internal Revenue Service",
        "development_levy": 10_000,
    },
    "Ebonyi": {
        "irs": "Ebonyi State Revenue Service",
        "development_levy": 3_000,
    },
    "Edo": {
        "irs": "Edo State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Ekiti": {
        "irs": "Ekiti State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Enugu": {
        "irs": "Enugu State Revenue Service",
        "development_levy": 5_000,
    },
    "FCT (Abuja)": {
        "irs": "FCT Internal Revenue Service",
        "development_levy": 10_000,
    },
    "Gombe": {
        "irs": "Gombe State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Imo": {
        "irs": "Imo State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Jigawa": {
        "irs": "Jigawa State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Kaduna": {
        "irs": "Kaduna State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Kano": {
        "irs": "Kano State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Katsina": {
        "irs": "Katsina State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Kebbi": {
        "irs": "Kebbi State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Kogi": {
        "irs": "Kogi State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Kwara": {
        "irs": "Kwara State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Lagos": {
        "irs": "Lagos State Internal Revenue Service (LIRS)",
        "development_levy": 20_000,
    },
    "Nasarawa": {
        "irs": "Nasarawa State Revenue Service",
        "development_levy": 3_000,
    },
    "Niger": {
        "irs": "Niger State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Ogun": {
        "irs": "Ogun State Revenue Service",
        "development_levy": 10_000,
    },
    "Ondo": {
        "irs": "Ondo State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Osun": {
        "irs": "Osun State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Oyo": {
        "irs": "Oyo State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Plateau": {
        "irs": "Plateau State Internal Revenue Service",
        "development_levy": 5_000,
    },
    "Rivers": {
        "irs": "Rivers State Internal Revenue Service",
        "development_levy": 15_000,
    },
    "Sokoto": {
        "irs": "Sokoto State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Taraba": {
        "irs": "Taraba State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Yobe": {
        "irs": "Yobe State Internal Revenue Service",
        "development_levy": 3_000,
    },
    "Zamfara": {
        "irs": "Zamfara State Internal Revenue Service",
        "development_levy": 3_000,
    },
}

ALL_STATES = sorted(STATE_DATA.keys())

DEFAULT_STATE = {
    "irs": "Federal Inland Revenue Service (FIRS)",
    "development_levy": 5_000,
}


def get_state_info(state: str) -> dict:
    return STATE_DATA.get(state, DEFAULT_STATE)
