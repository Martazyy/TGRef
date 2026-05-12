import pandas as pd

def load_products():
    df = pd.read_excel("products.xlsx")
    return df.to_dict(orient="records")


def get_categories(products):
    return sorted(list(set(p["category"] for p in products)))


def get_by_category(products, category):
    return [p for p in products if p["category"] == category]