"""
Retail Sales Analytics - Synthetic Dataset Generator
Generates a realistic, deterministic retail sales dataset with 2,500 transactions,
adhering strictly to relational integrity, realistic customer behaviors, and exact arithmetic rules.
"""

from datetime import datetime, timedelta
import random
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils import get_project_root, setup_logger

logger = setup_logger("data_generator")

PRODUCT_CATALOG = [
    # Electronics
    {"id": "PROD-EL-01", "name": "Wireless Noise-Canceling Headphones", "category": "Electronics", "unit_price": 149.99},
    {"id": "PROD-EL-02", "name": "4K Ultra HD Smart TV 55-inch", "category": "Electronics", "unit_price": 499.99},
    {"id": "PROD-EL-03", "name": "Bluetooth Portable Speaker", "category": "Electronics", "unit_price": 45.00},
    {"id": "PROD-EL-04", "name": "Ergonomic Mechanical Keyboard", "category": "Electronics", "unit_price": 89.50},
    {"id": "PROD-EL-05", "name": "Gaming Mouse with RGB Lighting", "category": "Electronics", "unit_price": 39.99},
    {"id": "PROD-EL-06", "name": "USB-C Multiport Adapter Hub", "category": "Electronics", "unit_price": 29.99},
    {"id": "PROD-EL-07", "name": "Smart Home Security Camera", "category": "Electronics", "unit_price": 79.99},
    {"id": "PROD-EL-08", "name": "Fast Wireless Charging Pad", "category": "Electronics", "unit_price": 24.99},

    # Apparel
    {"id": "PROD-AP-01", "name": "Classic Denim Jacket", "category": "Apparel", "unit_price": 68.00},
    {"id": "PROD-AP-02", "name": "Cotton Crewneck T-Shirt", "category": "Apparel", "unit_price": 19.50},
    {"id": "PROD-AP-03", "name": "Slim-Fit Chino Trousers", "category": "Apparel", "unit_price": 48.00},
    {"id": "PROD-AP-04", "name": "Waterproof All-Weather Parka", "category": "Apparel", "unit_price": 119.00},
    {"id": "PROD-AP-05", "name": "Merino Wool Knit Sweater", "category": "Apparel", "unit_price": 85.00},
    {"id": "PROD-AP-06", "name": "Athletic Running Shorts", "category": "Apparel", "unit_price": 32.00},
    {"id": "PROD-AP-07", "name": "Genuine Leather Dress Belt", "category": "Apparel", "unit_price": 35.00},
    {"id": "PROD-AP-08", "name": "Performance Cushioned Socks 3-Pack", "category": "Apparel", "unit_price": 15.00},

    # Home & Kitchen
    {"id": "PROD-HK-01", "name": "10-Piece Stainless Steel Cookware Set", "category": "Home & Kitchen", "unit_price": 189.99},
    {"id": "PROD-HK-02", "name": "Programmable Espresso Machine", "category": "Home & Kitchen", "unit_price": 229.00},
    {"id": "PROD-HK-03", "name": "Cold Brew Coffee Maker 1L", "category": "Home & Kitchen", "unit_price": 28.50},
    {"id": "PROD-HK-04", "name": "Non-Stick Ceramic Frying Pan", "category": "Home & Kitchen", "unit_price": 39.99},
    {"id": "PROD-HK-05", "name": "Organic Bamboo Cutting Board Set", "category": "Home & Kitchen", "unit_price": 25.00},
    {"id": "PROD-HK-06", "name": "High-Speed Countertop Blender", "category": "Home & Kitchen", "unit_price": 89.95},
    {"id": "PROD-HK-07", "name": "Insulated Thermal Tumbler 24oz", "category": "Home & Kitchen", "unit_price": 22.00},
    {"id": "PROD-HK-08", "name": "Air Fryer Max XL 5.8-Quart", "category": "Home & Kitchen", "unit_price": 99.99},

    # Beauty & Personal Care
    {"id": "PROD-BP-01", "name": "Hydrating Hyaluronic Acid Serum", "category": "Beauty & Personal Care", "unit_price": 34.00},
    {"id": "PROD-BP-02", "name": "Sonic Electric Toothbrush", "category": "Beauty & Personal Care", "unit_price": 59.99},
    {"id": "PROD-BP-03", "name": "Pure Moroccan Argan Hair Oil", "category": "Beauty & Personal Care", "unit_price": 24.50},
    {"id": "PROD-BP-04", "name": "Mineral Facial Sunscreen SPF 50", "category": "Beauty & Personal Care", "unit_price": 18.00},
    {"id": "PROD-BP-05", "name": "Ultrasonic Aromatherapy Diffuser", "category": "Beauty & Personal Care", "unit_price": 29.99},
    {"id": "PROD-BP-06", "name": "Dead Sea Mud Purifying Face Mask", "category": "Beauty & Personal Care", "unit_price": 21.00},
    {"id": "PROD-BP-07", "name": "Professional Ionic Hair Dryer", "category": "Beauty & Personal Care", "unit_price": 75.00},

    # Sports & Outdoors
    {"id": "PROD-SO-01", "name": "Non-Slip Eco Yoga Mat with Strap", "category": "Sports & Outdoors", "unit_price": 28.00},
    {"id": "PROD-SO-02", "name": "Adjustable Quick-Select Dumbbell Set", "category": "Sports & Outdoors", "unit_price": 149.00},
    {"id": "PROD-SO-03", "name": "Resistance Bands Workout Kit", "category": "Sports & Outdoors", "unit_price": 19.99},
    {"id": "PROD-SO-04", "name": "Insulated Outdoor Hydration Backpack", "category": "Sports & Outdoors", "unit_price": 42.00},
    {"id": "PROD-SO-05", "name": "Breathable Trail Running Shoes", "category": "Sports & Outdoors", "unit_price": 110.00},
    {"id": "PROD-SO-06", "name": "Heavy-Duty Foldable Camping Chair", "category": "Sports & Outdoors", "unit_price": 36.50},
    {"id": "PROD-SO-07", "name": "Smart GPS Fitness Tracker Band", "category": "Sports & Outdoors", "unit_price": 64.99},

    # Books & Media
    {"id": "PROD-BM-01", "name": "Data Science from Scratch Paperback", "category": "Books & Media", "unit_price": 38.50},
    {"id": "PROD-BM-02", "name": "Hands-On Machine Learning with Scikit-Learn", "category": "Books & Media", "unit_price": 49.99},
    {"id": "PROD-BM-03", "name": "The Lean Startup Hardcover", "category": "Books & Media", "unit_price": 27.00},
    {"id": "PROD-BM-04", "name": "Atomic Habits Hardcover Edition", "category": "Books & Media", "unit_price": 24.00},
    {"id": "PROD-BM-05", "name": "Deep Work by Cal Newport", "category": "Books & Media", "unit_price": 22.50},
    {"id": "PROD-BM-06", "name": "Science Fiction Award Anthology", "category": "Books & Media", "unit_price": 18.00},
]

REGIONS = ["North", "South", "East", "West", "Midwest"]
GENDERS = ["Male", "Female", "Non-Binary", "Prefer not to say"]
GENDER_WEIGHTS = [0.47, 0.47, 0.04, 0.02]
CUSTOMER_TYPES = ["Member", "Regular", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.45, 0.40, 0.15]

STORE_LOCATIONS = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Online Store"]
ORDER_STATUSES = ["Completed", "Returned", "Cancelled", "Pending"]
ORDER_STATUS_WEIGHTS = [0.91, 0.05, 0.03, 0.01]

DISCOUNT_TIERS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]
SALES_TAX_RATE = 0.08  # 8% standard sales tax


def generate_customer_profiles(num_customers: int = 500, seed: int = 42) -> dict:
    """Generates consistent customer demographic profiles."""
    random.seed(seed)
    np.random.seed(seed)
    
    customers = {}
    for i in range(1, num_customers + 1):
        cust_id = f"CUST-{1000 + i}"
        gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
        # Realistic age distribution between 18 and 74 (skewed towards 25-50)
        age = int(np.clip(np.random.normal(38, 12), 18, 74))
        region = random.choice(REGIONS)
        cust_type = random.choices(CUSTOMER_TYPES, weights=CUSTOMER_TYPE_WEIGHTS)[0]
        
        customers[cust_id] = {
            "customer_id": cust_id,
            "customer_gender": gender,
            "customer_age": age,
            "customer_region": region,
            "customer_type": cust_type,
        }
    return customers


def generate_dates(num_records: int = 2500, seed: int = 42) -> list[str]:
    """Generates dates in 2024 with realistic seasonal and day-of-week weighting."""
    random.seed(seed)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days + 1

    dates = []
    # Assign higher weights to November and December (holiday rush) and weekends (Sat/Sun)
    day_weights = []
    calendar_dates = [start_date + timedelta(days=d) for d in range(total_days)]

    for d in calendar_dates:
        weight = 1.0
        # Holiday shopping surge
        if d.month in [11, 12]:
            weight *= 1.65
        elif d.month in [7, 8]:  # Summer back-to-school / mid-year sales
            weight *= 1.2
        # Weekend boost (Friday, Saturday, Sunday)
        if d.weekday() in [4, 5, 6]:
            weight *= 1.35
        day_weights.append(weight)

    normalized_weights = np.array(day_weights) / sum(day_weights)
    chosen_indices = np.random.choice(len(calendar_dates), size=num_records, p=normalized_weights)
    chosen_dates = [calendar_dates[idx].strftime("%Y-%m-%d") for idx in chosen_indices]
    chosen_dates.sort()
    return chosen_dates


def generate_retail_sales_dataset(num_records: int = 2500, seed: int = 42) -> pd.DataFrame:
    """
    Synthesizes the complete retail sales dataset with 2,500 records.
    Ensures absolute mathematical precision and relational integrity.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    customers = generate_customer_profiles(num_customers=500, seed=seed)
    cust_id_list = list(customers.keys())
    dates = generate_dates(num_records=num_records, seed=seed)
    
    records = []
    
    for i in range(num_records):
        txn_id = f"TXN-{10001 + i}"
        txn_date = dates[i]
        
        # Pick customer (some repeat customers with higher probability)
        cust_id = random.choice(cust_id_list)
        cust_profile = customers[cust_id]
        
        # Pick product
        product = random.choice(PRODUCT_CATALOG)
        prod_id = product["id"]
        prod_name = product["name"]
        prod_cat = product["category"]
        unit_price = product["unit_price"]
        
        # Quantity purchased: mostly 1-3, occasionally up to 8
        quantity = int(np.random.choice([1, 2, 3, 4, 5, 6, 8], p=[0.55, 0.22, 0.12, 0.05, 0.03, 0.02, 0.01]))
        
        # Discount tier depends on customer type and promotions
        if cust_profile["customer_type"] == "VIP":
            disc_percent = random.choices([0.10, 0.15, 0.20, 0.25], weights=[0.3, 0.4, 0.2, 0.1])[0]
        elif cust_profile["customer_type"] == "Member":
            disc_percent = random.choices([0.00, 0.05, 0.10, 0.15], weights=[0.4, 0.3, 0.2, 0.1])[0]
        else:
            disc_percent = random.choices([0.00, 0.05, 0.10], weights=[0.7, 0.2, 0.1])[0]
            
        # Sales Channel
        sales_channel = random.choices(["Online", "In-Store", "Mobile App"], weights=[0.48, 0.32, 0.20])[0]
        
        # Store Location & Payment Method based on channel
        if sales_channel == "In-Store":
            store_loc = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
            payment_method = random.choices(
                ["Credit Card", "Debit Card", "Cash", "Digital Wallet"],
                weights=[0.45, 0.30, 0.15, 0.10]
            )[0]
        else:
            store_loc = "Online Store"
            payment_method = random.choices(
                ["Credit Card", "Debit Card", "PayPal", "Digital Wallet"],
                weights=[0.50, 0.25, 0.15, 0.10]
            )[0]
            
        order_status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS)[0]
        
        # Arithmetic calculations (strictly rounded to 2 decimal places)
        gross_amount = round(quantity * unit_price, 2)
        discount_amount = round(gross_amount * disc_percent, 2)
        taxable_amount = round(gross_amount - discount_amount, 2)
        tax_amount = round(taxable_amount * SALES_TAX_RATE, 2)
        total_amount = round(taxable_amount + tax_amount, 2)
        
        record = {
            "transaction_id": txn_id,
            "date": txn_date,
            "customer_id": cust_id,
            "customer_gender": cust_profile["customer_gender"],
            "customer_age": cust_profile["customer_age"],
            "customer_region": cust_profile["customer_region"],
            "customer_type": cust_profile["customer_type"],
            "product_id": prod_id,
            "product_category": prod_cat,
            "product_name": prod_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": disc_percent,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "sales_channel": sales_channel,
            "store_location": store_loc,
            "order_status": order_status,
        }
        records.append(record)
        
    df = pd.DataFrame(records)
    return df


def main():
    root = get_project_root()
    output_dir = root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "retail_sales.csv"
    
    logger.info("Generating Retail Sales dataset (2,500 records)...")
    df = generate_retail_sales_dataset(num_records=2500, seed=42)
    
    df.to_csv(output_file, index=False)
    logger.info(f"Successfully generated and saved dataset to: {output_file}")
    logger.info(f"Dataset Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    logger.info(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
