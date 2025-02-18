from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from products.urls import router as products_router
from orders.urls import router as orders_router
from cart.urls import router as cart_router

urlpatterns = [
    path('admin/', admin.site.urls),

    # products app
    path('api/', include(products_router.urls)),

    # orders app
    path('api/', include(orders_router.urls)),

    # cart
    path('api/', include(cart_router.urls)),

    # authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
