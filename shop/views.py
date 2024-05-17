from django_nextjs.render import render_nextjs_page
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from shop.serializers import ProductSerializer
from theme.pagination import make_pagination_class
from theme.utils import generate_excel_response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductSerializer.get_optimized_queryset()
    serializer_class = ProductSerializer
    pagination_class = make_pagination_class(cls_type="page_number", page_size=50)

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "brand__name",
        "category__name",
        "name",
    ]
    ordering_fields = ["pk", "price", "sale_price"]
    ordering = ["-pk"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.accepted_renderer.format == "xlsx":
            filename = "product_list.xlsx"
            return generate_excel_response(serializer.data, filename)
        else:
            response = super().list(request, *args, **kwargs)
            return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if request.accepted_renderer.format == "xlsx":
            filename = "product_detail.xlsx"
            return generate_excel_response(serializer.data, filename)
        else:
            response = super().retrieve(request, *args, **kwargs)
            return response


async def product(request):
    return await render_nextjs_page(request)
