from django.urls import path
from . import views
from base.urls import root_router


router = root_router
router.register(r"shop/product", views.ProductViewSet)

urlpatterns = [
    path("product/", views.product, name="product"),
]
