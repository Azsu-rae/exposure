import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store_service.settings')
django.setup()

from stores.models import Product
from users.models import Store, SellerProfile
from django.contrib.auth import get_user_model

def seed_database():
    User = get_user_model()
    
    print("Creating admin user 1...")
    admin_user1, created = User.objects.get_or_create(
        username='admin1',
        defaults={'email': 'admin1@example.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin_user1.set_password('admin123')
        admin_user1.save()
        admin_user1.activate_seller() # activates and makes SELLER
    
    seller1, _ = SellerProfile.objects.get_or_create(user=admin_user1, defaults={'is_verified': True})

    print("Creating admin user 2...")
    admin_user2, created = User.objects.get_or_create(
        username='admin2',
        defaults={'email': 'admin2@example.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin_user2.set_password('admin123')
        admin_user2.save()
        admin_user2.activate_seller()

    seller2, _ = SellerProfile.objects.get_or_create(user=admin_user2, defaults={'is_verified': True})


    print("Creating stores...")
    store1, _ = Store.objects.get_or_create(
        seller=seller1,
        defaults={'name': 'ElectroWorld', 'description': 'Best electronics in down!', 'city': 'Algiers'}
    )
    
    store2, _ = Store.objects.get_or_create(
        seller=seller2,
        defaults={'name': 'Fashion Hub', 'description': 'Trendy clothes and accessories.', 'city': 'Oran'}
    )
    
    print("Stores created")

    print("Creating products...")
    products = [
        {'name': 'Wireless Headphones', 'store': store1, 'price': 12500, 'stock': 50, 'description': 'Noise cancelling wireless headphones.'},
        {'name': 'Smartwatch Explorer', 'store': store1, 'price': 22000, 'stock': 30, 'description': 'Water resistant smartwatch with heart monitor.'},
        {'name': 'USB-C Hub Pro', 'store': store1, 'price': 4500, 'stock': 100, 'description': '7-in-1 USB hub adapter.'},
        
        {'name': 'Leather Jacket', 'store': store2, 'price': 18000, 'stock': 20, 'description': 'Genuine leather winter jacket.'},
        {'name': 'Running Sneakers', 'store': store2, 'price': 9500, 'stock': 45, 'description': 'Lightweight athletic running shoes.'},
        {'name': 'Silk Scarf', 'store': store2, 'price': 2500, 'stock': 80, 'description': 'Elegant silk scarf, perfect for summer.'},
    ]

    for p_data in products:
        Product.objects.get_or_create(
            name=p_data['name'], 
            store=p_data['store'],
            defaults={
                'price': p_data['price'],
                'stock': p_data['stock'],
                'description': p_data['description']
            }
        )
    print("Products created")
    print("Database seeded successfully! You can now run your Flutter App and test fetching.")

if __name__ == '__main__':
    seed_database()
