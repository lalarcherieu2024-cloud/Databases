from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from shop import views as shop_views

urlpatterns = [
    # Root URL redirects to the admin
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    # Custom admin pages MUST be listed BEFORE admin.site.urls
    path('admin/calendar/', shop_views.calendar_view, name='admin_calendar'),
    path('admin/calendar/events/', shop_views.calendar_events, name='admin_calendar_events'),
    path('admin/', admin.site.urls),
]
