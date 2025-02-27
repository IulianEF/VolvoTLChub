from app.models import db


class Consumable(db.Model):
    """
    ⚙️ Consumables used in repairs (e.g., oil, filters, brake pads).

    Attributes:
        id (int): Primary key.
        name (str): Name of the consumable item.
        quantity (int): Quantity available in stock.
        price_per_unit (float): Cost per unit of the consumable.
        threshold (int): Minimum quantity before restocking is triggered.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price_per_unit = db.Column(db.Float, default=0.0)
    threshold = db.Column(db.Integer, default=5)

    def __repr__(self):
        return f"<Consumable {self.name} - Qty: {self.quantity}>"