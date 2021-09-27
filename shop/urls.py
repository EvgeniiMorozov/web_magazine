from shop.views import test_view
from django.urls import path

urlpatterns = [
    path("", test_view, name='base')
    # path('admin/', admin.site.urls),
    # path('', include('shop.urls'))
]
