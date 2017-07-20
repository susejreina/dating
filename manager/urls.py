from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from . import views


app_name = 'manager'
urlpatterns = [
    url(r'^manager/$',
        views.IndexManager.as_view(),
        name='manager_index'),
    url(r'^manager/login$',
        views.LoginManager.as_view(),
        name='manager_login'),
    url(r'^manager/checkpoint$',
        views.CheckpointManager.as_view(),
        name='manager_checkpoint'),
    url(r'^manager/ajaxconnect$',
        login_required(views.ajax_connect),
        name='ajax_connect'),
    url(r'^manager/ajaxreplaceconnection$',
        login_required(views.ajax_replace_connection),
        name='ajax_replaceconnection'),
    url(r'^supervisor$',
        login_required(views.SupervisorView.as_view()),
        name='supervisor_panel'),
    url(r'^supervisor/newsfeed$',
        views.NewsFeedView.as_view(),
        name='supervisor_newsfeed'),
]
