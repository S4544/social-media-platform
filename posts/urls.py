from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('', views.feed, name='feed'),
    path('register/', views.register, name='register'),
    path('logout/', views.sign_out, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='posts/login.html'), name='login'),
    
    
    path('profile/<str:username>/', views.profile, name='profile'),
    path('search/', views.search, name='search'),

    
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    
    path('settings/', views.settings, name='settings'),
    path('account/delete/', views.delete_account, name='delete_account'),

 
    path('chat/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
]