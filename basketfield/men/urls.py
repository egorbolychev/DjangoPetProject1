from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import *

urlpatterns = [
    path('', cache_page(15)(MenHome.as_view()), name='home'),
    path('about/', About.as_view(), name='about'),
    path('add_page/', AddPage.as_view(), name='add_page'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', CreateAcc.as_view(), name='register'),
    path('post/<slug:post_slug>', SinglePost.as_view(), name='post'),
    path('category/<slug:cat_slug>', Categories.as_view(), name='category'),
    path('like/<int:pk>/', AddLike.as_view(model=Men), name='post_like'),
    path('dislike/<int:pk>/', AddDisLike.as_view(model=Men), name='post_dislike'),
]
