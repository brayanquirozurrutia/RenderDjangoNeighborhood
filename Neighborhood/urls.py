
from django.contrib import admin
from django.urls import path
from app1.views import changePasswordTemplate, createAccountTemplate, indexTemplate, homeTemplate, friendsTemplate, add_new_friend_template, edit_friend, alert_message, alert_summary, alert_detail, loginTemplate, logout_template, profile_template, restablecer_contraseña, activar_cuenta, account_created_template, expired_token_activate_account_template, account_not_activated_template, pending_password_change_template, password_changed_template

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', indexTemplate, name='index'),
    path('login/', loginTemplate, name='login'),
    path('create-account/', createAccountTemplate, name='create_account'),
    path('account_created/', account_created_template, name='account_created'),
    path('expired_token_activate_account/', expired_token_activate_account_template, name='expired_token_activate_account'),
    path('account_not_activated/', account_not_activated_template, name='account_not_activated'),
    path('activate_account/<str:token>/', activar_cuenta, name='activar_cuenta'),
    path('change-password/', changePasswordTemplate, name='change_password'),
    path('pending_password_change/', pending_password_change_template, name='pending_password_change'),
    path('reset_password/<str:token>/', restablecer_contraseña, name='restablecer_contraseña'),
    path("password_changed", password_changed_template, name="password_changed"),
    path('home/', homeTemplate, name='home'),
    path('home/friends/', friendsTemplate, name='friends'),
    path('home/friends/new-friend', add_new_friend_template, name='new_friend'),
    path('home/friends/edit-friend', edit_friend, name='edit_friend'),
    path('home/alert_mesage', alert_message, name='alert_message'),
    path('home/alert_summary', alert_summary, name='alert_summary'),
    path('home/alert_summary/alert_detail', alert_detail, name='alert_detail'),
    path('home/profile/', profile_template, name='profile'),
    path('logout/', logout_template, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
