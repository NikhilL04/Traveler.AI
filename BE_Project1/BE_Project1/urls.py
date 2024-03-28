"""BE_Project1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from travelapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',views.home_page,name="home"),
    path('get_destinations', views.get_Destinations, name='get_Destinations'),
    path('get_weather/<str:city>/', views.get_weather, name='get_weather'),
    path('currentweather/<str:city>/',views.getcurrent_weather,name="currentweather"),
    path('travelAi/', views.travelAi, name='travelAi'),
    path('new_chat/', views.new_chat, name='new_chat'),
    path('error-handler/', views.error_handler, name='error_handler'),
    path('getplaces/', views.upload_Form, name="getplaces"),
    path('veruser/', views.ver_user, name="veruser"),
    path('hotel_list/', views.hotel_list,name='hotel_list'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.logged,name='login')


]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
