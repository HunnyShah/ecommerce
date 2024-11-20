from django.core.management.base import BaseCommand
from store.models import Product, Category
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample products'

    def handle(self, *args, **kwargs):
        category = Category.objects.first()  # Assuming at least one category exists

        # Hardcoded products
        products = [
            ('Product 1', 'Description of product 1', Decimal('19.99'), 100, category),
            ('Product 2', 'Description of product 2', Decimal('29.99'), 200, category),
            ('Product 3', 'Description of product 3', Decimal('39.99'), 150, category),
            ('Product 4', 'Description of product 4', Decimal('49.99'), 50, category),
            ('Product 5', 'Description of product 5', Decimal('59.99'), 30, category),
            ('Product 6', 'Description of product 6', Decimal('69.99'), 20, category),
            ('Product 7', 'Description of product 7', Decimal('79.99'), 10, category),
            ('Product 8', 'Description of product 8', Decimal('89.99'), 15, category),
            ('Product 9', 'Description of product 9', Decimal('99.99'), 40, category),
            ('Product 10', 'Description of product 10', Decimal('109.99'), 25, category),
        ]

        for product_data in products:
            product = Product(
                name=product_data[0],
                description=product_data[1],
                price=product_data[2],
                stock_quantity=product_data[3],
                category=product_data[4],
                image_url='http://example.com/product-image.jpg'  # Placeholder image URL
            )
            product.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 10 sample products'))
