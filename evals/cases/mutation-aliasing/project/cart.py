class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, category, price):
        self.items.append({"name": name, "category": category, "price": price})

    def get_items(self):
        return self.items

    def total(self):
        return round(sum(item["price"] for item in self.items), 2)
