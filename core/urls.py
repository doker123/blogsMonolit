from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('profile/<int:user_id>/', views.profile_view, name='profile'),
    # path('profile/edit/', views.edit_profile, name='edit_profile'),
    # path('profile/delete/', views.delete_profile, name='delete_profile'),
    # path('create/', views.create_post, name='create_post'),
    # path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    # path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    # path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    # path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    # path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]