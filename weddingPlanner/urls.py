from django.conf.urls import include, url # pragma: no cover
from django.contrib import admin # pragma: no cover
from weddingServices import views as ws_views # pragma: no cover
from django.contrib.auth import views as auth_views # pragma: no cover


urlpatterns = [ # pragma: no cover
    # Examples:
    # url(r'^$', 'weddingPlanner.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^login/$', auth_views.login, {'template_name': 'weddingServices/login.html'}, name='login'),
	url(r'^logout/$', auth_views.logout, {'next_page': '/weddingServices'}, name='logout'),
	url(r'^signup/$', ws_views.signup, name='signup'),
	url(r'^weddingServices/', include('weddingServices.urls')),
]
