from django.urls import path

from users.views import registration_view, index, logout_view, login_view, account_view, must_authenticate_view, server_registration_view, server_update, server_update_view, server_delete

app_name = 'users'
urlpatterns = [
    path('', index, name='index'),
    path('detail/', account_view, name='account'),
    path('detail/server_reg/', server_registration_view, name='server_registration'),
    path('<int:listz_id>/server_updatev/', server_update_view, name='server_update_view'),
    path('<int:listz_id>/server_update/', server_update, name='server_update'),
    path('<int:listz_id>/server_delete/', server_delete, name='server_delete'),
    path('login/', login_view, name='login'),
    path('must_authenticate/', must_authenticate_view, name='must_authenticate'),
    path('register/', registration_view, name='registration_view'),
    path('logout/', logout_view, name='logout'),

]