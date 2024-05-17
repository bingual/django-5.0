from django.contrib import admin

from shop.models import Brand, BrandThumbnail, Category, Product


# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(BrandThumbnail)
class BrandThumbnailAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
