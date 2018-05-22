from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from .forms import FaceAuthenticationForm

urlpatterns = [
    # path('accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.home, name='home'),
    url(r'^personal/$', views.personal_notes, name='personal'),
    url(r'^note/$', views.add_note, name='add_note'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html', 'authentication_form': FaceAuthenticationForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
]