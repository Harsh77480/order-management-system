from pyclbr import Class
from django.db.models import Max, Avg
from django.shortcuts import get_object_or_404
from api.serializers import OrderCreateSerializer, ProductSerializer, OrderSerializer, ProductInfoSerializer
from api.models import Product, Order, OrderItem
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated as isAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny 
from .filters import OrderFilters, ProductFilters
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.decorators import action

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

    # if request.method == 'GET':
    #     return Response({"message": "GET logic"})
    
    #  elif request.method == 'POST':
    #     return Response({"message": "POST logic"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items','items__product').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })
    return Response(serializer.data)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [isAuthenticated] 

    def get_permissions(self):
        print(self.request.method)
        self.permission_classes = [AllowAny] if self.request.method == 'GET' else [isAuthenticated] 
        return super().get_permissions()
        
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items','items__product').all()
    serializer_class = OrderSerializer 
    permission_classes = [isAuthenticated] 

class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('items','items__product')
    permission_classes = [isAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)
    
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [ProductFilters] 
    pagination_class = PageNumberPagination
    pagination_class.page_size = 4
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 10

    def get_queryset(self): # this will be called before filter_backends 
        queryset = super().get_queryset() # we can't use self.get_queryset() here as it will cause infinite recursion 
        queryset = queryset.annotate(review=Avg('reviews__rating'))
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items','items__product').all()
    serializer_class = OrderSerializer
    filter_backends = [OrderFilters]
    
    @action(detail=False, methods=['get'], url_path='user-orders', permission_classes=[isAuthenticated])
    def user_orders(self, request):    
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    def get_serializer(self, *args, **kwargs):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update': # partial_update method is for PATCH 
            kwargs['context'] = self.get_serializer_context() # context is accesible as self.context.get() inside serializer 
            return OrderCreateSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 
