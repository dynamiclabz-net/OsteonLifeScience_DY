from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

admin.site.site_header = "Osteon Life Science"
admin.site.site_title = "Osteon Admin"
admin.site.index_title = "Website management"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('FrontEnd.urls')),
    path('user-api/', include('UserDetail.urls')),
    path('catalog-api/', include('Catalog.urls')),
    path('site-content-api/', include('SiteContent.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
