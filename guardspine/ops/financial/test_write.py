
import math
import sys

TIERS = {
    "Pro":        {"price_mo": 2000,  "cogs_mo": 250,  "cac": 5000,  "nrr": 1.15},
    "Business":   {"price_mo": 5000,  "cogs_mo": 500,  "cac": 15000, "nrr": 1.20},
    "Enterprise": {"price_mo": 12000, "cogs_mo": 1050, "cac": 50000, "nrr": 1.30},
}
print('Constants loaded:', list(TIERS.keys()))
