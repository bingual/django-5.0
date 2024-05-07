import openpyxl
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.response import Response

from shop.serializers import ProductSerializer
from theme.utils import create_excel_file


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductSerializer.get_optimized_queryset()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        if request.accepted_renderer.format == "xlsx":
            filename = "product_list.xlsx"
            excel_file = create_excel_file(serializer.data, filename)
            response = FileResponse(
                excel_file,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        else:
            return Response(serializer.data)
