from decimal import Decimal
from stores.models import Order

STORES = {
    "abdellaoui_mohamed": [
        {
            "name": "Rouiba Market",
            "description": "Neighbourhood grocery store",
            "wilaya": "Alger",
            "city": "Rouiba",
        },
        {
            "name": "Green Grocers",
            "description": "Fresh organic vegetables and fruits",
            "wilaya": "Annaba",
            "city": "Annaba",
        },
    ],
    "gaceb_hicham": [
        {
            "name": "Tech Gadgets Hub",
            "description": "Latest electronics and gadgets",
            "wilaya": "Alger",
            "city": "Algiers",
        },
    ],
    "benali_sara": [
        {
            "name": "Sara's Bakery",
            "description": "Freshly baked goods every morning",
            "wilaya": "Oran",
            "city": "Oran",
        },
        {
            "name": "Fresh Catch Seafood",
            "description": "Daily catch straight from the coast",
            "wilaya": "Béjaïa",
            "city": "Bejaia",
        },
    ],
    "meziane_karim": [
        {
            "name": "Karim Electronics",
            "description": "PC components and peripherals",
            "wilaya": "Constantine",
            "city": "Constantine",
        },
    ],
}

PRODUCTS = {
    "Rouiba Market": [
        {"name": "Bread Loaf",  "description": "Freshly baked white bread",
            "price": Decimal("1.20"), "stock": 100},
        {"name": "Whole Milk",
            "description": "Full-fat cow's milk (1L)",            "price": Decimal("0.90"), "stock": 150},
        {"name": "Eggs",
            "description": "Free-range eggs (pack of 12)",        "price": Decimal("2.50"), "stock": 75},
        {"name": "Olive Oil",
            "description": "Extra-virgin olive oil (750ml)",      "price": Decimal("6.99"), "stock": 60},
    ],
    "Green Grocers": [
        {"name": "Organic Apples", "description": "Fresh red apples (1kg)",           "price": Decimal(
            "3.99"), "stock": 200},
        {"name": "Avocados",       "description": "Ripe Hass avocados (pack of 3)",   "price": Decimal(
            "5.49"), "stock": 80},
        {"name": "Carrots",        "description": "Organic carrots (1kg)",            "price": Decimal(
            "1.80"), "stock": 120},
        {"name": "Tomatoes",
            "description": "Vine-ripened tomatoes (500g)",     "price": Decimal("2.20"), "stock": 90},
    ],
    "Tech Gadgets Hub": [
        {"name": "Wireless Earbuds",  "description": "Bluetooth 5.0 earbuds",
            "price": Decimal("49.99"),  "stock": 30},
        {"name": "Smart Watch",       "description": "Fitness tracking smartwatch",
            "price": Decimal("199.99"), "stock": 15},
        {"name": "USB-C Hub",         "description": "7-in-1 USB-C adapter",
            "price": Decimal("29.99"),  "stock": 40},
        {"name": "Portable Charger",  "description": "20000mAh power bank",
            "price": Decimal("39.99"),  "stock": 25},
    ],
    "Sara's Bakery": [
        {"name": "Croissant",       "description": "Buttery French croissant",
            "price": Decimal("1.50"), "stock": 80},
        {"name": "Baguette",        "description": "Classic French baguette",
            "price": Decimal("1.00"), "stock": 60},
        {"name": "Almond Cake",     "description": "Moist almond and honey cake (slice)",    "price": Decimal(
            "3.50"), "stock": 40},
        {"name": "Chocolate Muffin", "description": "Double chocolate chip muffin",
            "price": Decimal("2.00"), "stock": 50},
    ],
    "Fresh Catch Seafood": [
        {"name": "Sardines", "description": "Fresh whole sardines (1kg)",        "price": Decimal(
            "4.50"),  "stock": 70},
        {"name": "Shrimp",   "description": "Peeled king shrimp (500g)",         "price": Decimal(
            "12.99"), "stock": 35},
        {"name": "Sea Bass", "description": "Whole sea bass, gutted and scaled",
            "price": Decimal("9.99"),  "stock": 20},
    ],
    "Karim Electronics": [
        {"name": "Gaming Mouse",        "description": "RGB optical gaming mouse, 12000 DPI",
            "price": Decimal("34.99"), "stock": 45},
        {"name": "Mechanical Keyboard", "description": "TKL mechanical keyboard, brown switches",
            "price": Decimal("79.99"), "stock": 20},
        {"name": "Monitor Stand",       "description": "Adjustable dual-monitor stand",
            "price": Decimal("49.99"), "stock": 15},
        {"name": "Webcam",              "description": "1080p HD webcam with built-in mic",
            "price": Decimal("44.99"), "stock": 30},
    ],
}

ORDERS = {
    "abdellaoui_mohamed": [
        {
            "status": Order.StatusChoices.CONFIRMED,
            "items": [
                {"product": "Wireless Earbuds", "quantity": 1},
                {"product": "Smart Watch",      "quantity": 2},
                {"product": "Avocados",         "quantity": 3},
                {"product": "Whole Milk",       "quantity": 1},
            ],
        },
        {
            "status": Order.StatusChoices.CANCELLED,
            "items": [],
        },
    ],
    "gaceb_hicham": [
        {
            "status": Order.StatusChoices.PENDING,
            "items": [
                {"product": "Organic Apples", "quantity": 2},
                {"product": "Bread Loaf",     "quantity": 3},
            ],
        },
        {
            "status": Order.StatusChoices.CONFIRMED,
            "items": [
                {"product": "Croissant",   "quantity": 4},
                {"product": "Almond Cake", "quantity": 2},
            ],
        },
    ],
    "benali_sara": [
        {
            "status": Order.StatusChoices.CONFIRMED,
            "items": [
                {"product": "USB-C Hub",    "quantity": 1},
                {"product": "Gaming Mouse", "quantity": 1},
            ],
        },
        {
            "status": Order.StatusChoices.PENDING,
            "items": [
                {"product": "Tomatoes",  "quantity": 3},
                {"product": "Carrots",   "quantity": 2},
                {"product": "Olive Oil", "quantity": 1},
            ],
        },
    ],
    "meziane_karim": [
        {
            "status": Order.StatusChoices.PENDING,
            "items": [
                {"product": "Eggs",       "quantity": 2},
                {"product": "Whole Milk", "quantity": 3},
                {"product": "Bread Loaf", "quantity": 1},
            ],
        },
        {
            "status": Order.StatusChoices.CONFIRMED,
            "items": [
                {"product": "Sardines", "quantity": 4},
                {"product": "Shrimp",   "quantity": 2},
            ],
        },
    ],
}
