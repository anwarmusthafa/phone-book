from django.urls import path
from .views import LoginView, RegisterView, HomeView, AddContactView, SpamReportView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', HomeView.as_view(), name='home'),
    path('add-contact/', AddContactView.as_view(), name='add-contact'),
    path('spam-report/', SpamReportView.as_view(), name='spam-report'),

]
