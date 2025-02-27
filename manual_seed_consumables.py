"""
manual_seed_consumables.py

This script seeds the Consumable table with 20 random items.
Run it once after creating your database to populate initial stock.
"""

import random
import string
from app.db_setup import create_app, db
from app.models.consumable import Consumable


def generate_random_name():
    """
    🔤 Generates a short random name then appends a 3-letter random uppercase suffix for uniqueness.
    example -> "Oil_AHZ" or "Filter_GXQ"
    You can customize this for more variety.
    """
    prefix = random.choice(["Oil", "Filter", "BrakePads", "Coolant", "Wipers",
                            "SparkPlugs", "Tires", "Antifreeze", "Headlight",
                            "AirFilter", "BrakeFluid", "TransmissionFluid",
                            "Battery", "RadiatorCap", "EngineOil", "Bulbs",
                            "PowerSteeringFluid", "Fuse", "TimingBelt", "Grease"])
    suffix = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{prefix}_{suffix}"


def generate_random_consumable():
    """
    🛢️ Creates a single Consumable with random attributes.
    """
    # random name (unique if possible, but collisions may be rare with suffix)
    name = generate_random_name()
    quantity = random.randint(0, 100)  # from 0 to 100
    price_per_unit = round(random.uniform(1.0, 50.0), 2)  # random price
    threshold = random.randint(5, 15)  # minimum stock

    return Consumable(
        name=name,
        quantity=quantity,
        price_per_unit=price_per_unit,
        threshold=threshold
    )


def seed_consumables(count=20):
    """
    🚚 Seeds the database with 'count' random consumables.
    Avoids duplicates by checking the name before insertion.
    """
    app = create_app()
    with app.app_context():
        # For demonstration, we won't ensure perfect uniqueness,
        # but if a collision occurs, we simply skip or regenerate.
        existing_names = set(c.name for c in Consumable.query.all())

        items_added = 0
        for _ in range(count):
            item = generate_random_consumable()
            # If there's a collision in the name, just skip or re-generate
            if item.name in existing_names:
                continue  # skip duplicates
            db.session.add(item)
            existing_names.add(item.name)
            items_added += 1

        db.session.commit()
        print(f"✅ Added {items_added} new consumables to the database.")


if __name__ == "__main__":
    seed_consumables(20)
