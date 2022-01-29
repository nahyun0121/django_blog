from django.urls import path
from . import views

urlpatterns = [
    path('category/<str:slug>/', views.category_page),          # 'slug/'만 떼어 category_page() 함수로 보냄
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index),
]