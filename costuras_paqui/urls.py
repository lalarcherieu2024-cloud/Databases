from django.contrib import admin
from django.urls import path

from shop import views as shop_views

urlpatterns = [
    # Custom admin pages MUST be listed BEFORE admin.site.urls
    # so Django matches them first
    path('admin/calendar/', shop_views.calendar_view, name='admin_calendar'),
    path('admin/calendar/events/', shop_views.calendar_events, name='admin_calendar_events'),
    path('admin/', admin.site.urls),
]