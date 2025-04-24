from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Начальная точка входа
    path('', views.root_redirect, name='root'),

    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Главная и действия
    path('home/', views.home_view, name='home'),
    path('create/<int:emotion_id>/', views.create_mood_view, name='create_mood'),
    path('entry/<int:year>/<int:month>/<int:day>/', views.mood_entry_detail, name='entry_detail'),

    # Календарь и профиль
    path('history/', views.mood_history_view, name='history'),
    path('profile/', views.profile_view, name='profile'),

    # Сброс пароля по email
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='mood/password_reset.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='mood/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='mood/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='mood/password_reset_complete.html'
    ), name='password_reset_complete'),
]