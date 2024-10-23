from django.urls import path
from .views import (
    home, 
    chatbot, 
    chat_api,
    register,
    login_view,
    farmer_dashboard,
    get_suggestions,
    LogoutThankYouView,
    CustomLogoutView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('chatbot/', chatbot, name='chatbot'),
    path('chat_api/', chat_api, name='chat_api'),
    path('register/', register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # Ensure as_view() is called only once
    path('logout-thank-you/', LogoutThankYouView.as_view(), name='logout_thank_you'),
    path('login/', login_view, name='login'),
    path('get_suggestions/', get_suggestions, name='get_suggestions'),
    path('dashboard/',farmer_dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
