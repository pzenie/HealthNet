from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^(\d+)/$", name="main"),
    url(r"", name="main"),
    url(r"^month/(\d+)/(\d+)/(prev|next)/$", name="month"),
    url(r"^month/(\d+)/(\d+)/$", name="month"),
    url(r"^month$", name="month"),
    url(r"^day/(\d+)/(\d+)/(\d+)/$", name="day"),
    ]
