from django.db.models import QuerySet
from rest_framework import serializers

from shop.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["pk", "brand", "category", "thumb", "name", "price", "sale_price"]

    @staticmethod
    def get_optimized_queryset() -> QuerySet[Product]:
        return Product.objects.all().only(
            "pk", "brand", "category", "thumb", "name", "price", "sale_price"
        )
