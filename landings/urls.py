from django.conf.urls import url
from . import views

app_name = 'landings'
urlpatterns = [
    url(r'^lp/(?P<slug>\w+)/$', views.landing_page_form, name='landing'),
    url(r'^landing/form/validate', views.validate_form, name='validate_form'),
]
