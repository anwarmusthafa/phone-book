from django.urls import path
from .views import LoginView, RegisterView, HomeView, ContactView, SpamReportView, SearchByPhoneNumberView, SearchByNameView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', HomeView.as_view(), name='home'),
    path('contact/', ContactView.as_view(), name='add-contact'),
    path('spam-report/', SpamReportView.as_view(), name='spam-report'),
    path('search-by-number/<str:phone_number>/', SearchByPhoneNumberView.as_view(), name='search-by-number'),
    path('search-by-name/<str:name>/', SearchByNameView.as_view(), name='search-by-name'),


]
