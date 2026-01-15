from django.urls import path
from . import views

# Define URL patterns for the API endpoints
# For each endpoint, we have both function-based and class-based views

urlpatterns = [
    path('products/', views.ProductListCreateView.as_view()),
    path('products/', views.product_list),
    path('products/', views.ProductListView.as_view()),

    path('products/info/', views.ProductInfoAPIView.as_view()),
    path('products/info/', views.product_info),

    path('products/<int:pk>/', views.ProductDetailView.as_view()),
    path('products/<int:pk>/', views.product_detail),
 
    path('orders/', views.OrderListView.as_view()),
    path('orders/', views.order_list),

    path('user/orders/', views.UserOrderListView.as_view()),    
]