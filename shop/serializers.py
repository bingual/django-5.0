from django.db.models import QuerySet
from rest_framework import serializers

from shop.models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    brand = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            "url",
            "pk",
            "brand",
            "category",
            "thumb",
            "name",
            "price",
            "sale_price",
        ]

    @staticmethod
    def get_optimized_queryset() -> QuerySet[Product]:
        return Product.objects.select_related("brand", "category").only(
            "pk",
            "brand__name",
            "category__name",
            "thumb",
            "name",
            "price",
            "sale_price",
        )
