import pandas as pd

from backend.app.config import DATA_DIR
from backend.app.models import Product, Restaurant


def seed_master_data(db):
    if db.query(Restaurant).count() > 0:
        return

    restaurant_file = DATA_DIR / "swiggy_dim_restaurant_location.xlsx"
    menu_file = DATA_DIR / "swiggy_dim_restaurant_menu_enriched.xlsx"

    if restaurant_file.exists() and menu_file.exists():
        restaurant_df = pd.read_excel(restaurant_file)
        menu_df = pd.read_excel(menu_file)

        restaurant_df = restaurant_df.loc[:, ~restaurant_df.columns.duplicated()]
        menu_df = menu_df.loc[:, ~menu_df.columns.duplicated()]

        for _, row in restaurant_df.iterrows():
            restaurant = Restaurant(
                restaurant_id=int(row["restaurant_id"]),
                restaurant_name=str(row["restaurant_name"]),
                cuisine_tag=str(row.get("cuisine_tag", "Food")),
                city=str(row.get("city", "Hyderabad")),
                location_name=str(row.get("restaurant_location_name", row["restaurant_name"])),
                address=str(row.get("restaurant_address", "Hyderabad")),
                area=str(row.get("restaurant_area", row.get("area_name", ""))),
                pincode=str(row.get("restaurant_pincode", "")),
                restaurant_latitude=float(row["restaurant_latitude"]),
                restaurant_longitude=float(row["restaurant_longitude"]),
                rating=float(row.get("rating", 4.2)),
                cost_for_two=float(row.get("cost_for_two", 400)),
                default_prep_minutes=int(row.get("default_prep_minutes", 25)),
                is_active=int(row.get("is_active", 1)),
                location_source=str(row.get("location_source", "excel_enriched")),
            )

            db.add(restaurant)

        db.commit()

        for _, row in menu_df.iterrows():
            product = Product(
                restaurant_id=int(row["restaurant_id"]),
                product_name=str(row.get("product_name", "Special Item")),
                price=float(row.get("list_price", 250)),
                cuisine_tag=str(row.get("cuisine_tag", "Food")),
                food_type=str(row.get("food_type", "Veg")),
                description=f"{row.get('product_name', 'Special Item')} from {row.get('restaurant_name', '')}",
                is_available=int(row.get("is_available", 1)),
            )

            db.add(product)

        db.commit()

        print("Seeded restaurants and menu from enriched Excel files.")
        return

    fallback_restaurants = [
        Restaurant(
            restaurant_id=1,
            restaurant_name="Paradise - Dilsukhnagar Colony",
            cuisine_tag="Biryani",
            city="Hyderabad",
            location_name="Paradise - Dilsukhnagar Colony",
            address="Dilsukhnagar Colony, Hyderabad, Telangana",
            area="Dilsukhnagar Colony",
            pincode="500060",
            restaurant_latitude=17.3717,
            restaurant_longitude=78.5272,
            rating=4.4,
            cost_for_two=500,
            default_prep_minutes=25,
            location_source="fallback",
        )
    ]

    db.add_all(fallback_restaurants)
    db.commit()

    fallback_products = [
        Product(
            restaurant_id=1,
            product_name="Chicken Biryani",
            price=320,
            cuisine_tag="Biryani",
            food_type="Non-Veg",
            description="Classic Hyderabadi chicken biryani",
        ),
        Product(
            restaurant_id=1,
            product_name="Paneer Biryani",
            price=280,
            cuisine_tag="Biryani",
            food_type="Veg",
            description="Paneer biryani with raita",
        ),
    ]

    db.add_all(fallback_products)
    db.commit()

    print("Seeded fallback restaurant/menu data.")