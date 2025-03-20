from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from products.urls import router as products_router
from orders.urls import router as orders_router
from cart.urls import router as cart_router
from payments.urls import router as payment_router

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('admin/', admin.site.urls),

    # products app
    path('api/', include(products_router.urls)),

    # orders app
    path('api/', include(orders_router.urls)),

    # cart
    path('api/', include(cart_router.urls)),

    # payment
    path('api/', include(payment_router.urls)),
    path('', include('payments.urls')),

    # authentication
    path('topnotch/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),

    # Password Reset
    path('api/auth/password/reset/',
         PasswordResetView.as_view(), name='password_reset'),
    path('reset/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
