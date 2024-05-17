from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django_nextjs.render import render_nextjs_page
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

root_router = routers.DefaultRouter()


async def root(request):
    return await render_nextjs_page(request)


urlpatterns = [
    # local apps
    path("", root),
    path(settings.ADMIN_PREFIX, admin.site.urls),
    path(
        "admin/",
        include(
            "admin_honeypot.urls",
        ),
    ),
    path("accounts/", include("accounts.urls")),
    path("photolog/", include("photolog.urls")),
    path("shop/", include("shop.urls")),
    # api
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/", include(root_router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# pillow
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if apps.is_installed("debug_toolbar"):
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

if apps.is_installed("django_browser_reload"):
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
