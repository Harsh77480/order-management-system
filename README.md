
***This repository serves as a learning and revision resource for implementing Django REST Framework.***

## Setup 
```
Python 3.14.2 
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Pull from Git or do :
```
Create a local folder 'Project Name'
django-admin startproject config .
python manage.py startapp api
Add 'api' in installed_apps in settings.py 
```

Convention is to name django project `config` and have outer local folder name as the actual project name.


```
python manage.py makemigrations -> migrate
python manage.py createsuperuser
python manage.py populate_db 
```
api\management\populate_db.py is custom script for creating dummy instances


`Resources` 
- [YT](https://www.youtube.com/watch?v=6AEvlNgRPNc&list=PL-2EBeDYMIbTLulc9FSoAXhbmXpLq2l5t)

- [CDRF](https://www.cdrf.co/)


## Desgining flow

[models](https://github.com/Harsh77480/order-management-system/blob/master/api/models.py)

***DRF URLs returns a browsable page if you open them in browser***

### \api\views.py  
`product_list()`
- uses @api_view decorater with ['GET'] input, we can also add PUT, POST, etc in this array too. because of @api_view, we need to pass query param ?format=json for pure json response. 
- using ProductSerializer() with param many=True, since we are using it for listing. 

### \api\serializers.py
`OrderSerializer()`
- IMP : `related_name` param in ForeignKey field is the field by which ForeignKey reference table (usually parent) access the current table(child) in which ForeignKey is defined.

- this is the `NESTED` serializer with OrderItemSerializer as a serializer field 

- for this to work, field name of child serializer(OrderItemSerializer) in parent Serializer(OrderSerializer), must be same as `related_name` (items, in our case) 

- `field_name` = SerializerMethodField(), is custom field (not a model field) which can be used to return any type of logic. Just define a method in your serializer as get_`field_name`() to calculate the logic. This method accepts self and obj, obj being an instance of `Model` used in current serializer. Like we have created total_price field. ***This receives (self,instance)***
    

`OrderItemSerializer()` 
- we can have serializer fields CharField and DecimalField, just like model and also define the source(model field) from which we want to populate it(product.name).
- we can also add model method (item_subtotal) in serializer field list 


### \api\view.py
` product_info() `
- this uses `generic` serialzier not related to any model 
- the queryset that this serializer takes, must have the fields that are defined in generic serializer 
- we have used a model serializer as nested serializer inside `generic` serializer 
- http://127.0.0.1:8000/api/products/info/ 


### pip install django-silk
- add it in installed apps and in middleware(after SecurityMiddleware)

- add in main urls.py

- now if we hit an end point like http://127.0.0.1:8000/api/orders/

- then go to http://127.0.0.1:8000/silk/ it give all info about the speed, sql, etc. about that api call  

- we can see in sql tab that /orders api is hitting `20 sql queries` which very bad, this is becuse we have passed queryset to a nested model serializer without prefetch related.

### \api\views.py 
`order_list()` 
- using prefetch related to fetch all the order items info and all the products info related to those items in single query.

- hit the /orders url again and see the sql in silk, we have optimized from `20 queries to 5 queries`


### \api\views.py 
- added generic class based views 

### \api\admin.py 
- we can modify admin view of a model here.
- used inline to attach child view (OrderItem) table to parent view(Order) using `inline`


### \api\views.py 
`UserOrderListView()` 
- made to fetch only the orders of requesting user 

- overrided get_queryset method to return the queyset filtered by request.user 

- request.user returns `AnonymousUser` if you have not logged into django admin 

- permission_classes = [isAuthenticated], lets you access this api only if you logged into djanog admin. We also have isAdminUser and AllowAny

- We can overide `get_permissions`() for custom permissions   

***get_permissions is improtant***



### Mixins : `IMPORTANT` 
- There are 5 mixins in drf (CreateModelMixin,ListModelMixin,RetriveModelMixin,DestoryModelMixin,UpdateModelMixin) 

- Each mixin is a class that provide methods like create, list, update, retrive and delete

- APIView, generic Views, etc. inherit these mixins.

- The `default create` method in CreateModelMixin : ***IMPORTANT***
````
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
````

### The sequence of important methods : 
When we send a POST request to a DRF endpoint (`VIEW`), it triggers the `create action`. Then these methods are called in follow sequence from the `VIEW` inside `create()`

-> `create(self, request, *args, **kwargs)` : this is the manager method. 

-> `get_serializer(self, *args, **kwargs)` : with request.data 

-> `serializer.is_valid()` 

-> `perform_create (self, serializer)` : this is specifically designed to override withoud breaking the whole create logic.

-> `serializer.save(**kwargs)` : (called from perform_create) this dertermines whether to call .create() or .update() inside the serializer.




### \api\views.py 
`ProductInfoAPIView()`
- is an APIView, which very powerfull since we can override get, post, etc. to write custom logic. 

`ProductListCreateView()`
- is a generics.ListCreateView. `ListCreateView inherits both ListModelMixin and CreateModelMixin`

- `when we go to \products we get the list as well as a create form` 

- this way we can use \products for both listing products and creating products. ` This follows the rest convention `


 ### pip install djangorestframework-simplejwt

 - configure settings.py to add JWTAuthentication (add before SessionAuthentication so thatSessionAuthentication acts as fallback)
 - configure main urls.py to add TokenObtainPairView and TokenRefreshView urls

 - If we hit post request on `api/token` with django user's credentials in json body, we will get the `refresh` and `access token`

 - we can use access token as Bearer token for authorizaiton when calling all apis 

- we can use the refresh token to refresh the access token by calling 
`api/token/refresh` with json body as "refresh" : refres token





### \api\views 
`ProductDetailView()`
- is a RetrieveUpdateDestroyAPIView, which inherits 3 mixins 
- we create, retrive, update product from same sapi /products/id, based on the http method. 
- `This way we can allow the rest api naming convention` 
- overided get_permission(), for custom permission, if method is GET user don't need to be logged in. 


### \api\filters 
`ProductFilters()` 

- instead of overriding get_querset() in generic views for ordering and filtering, we can use rest_framework's filter.BaseFilterBackend 

- we have created class ProductFilters which inherits from BaseFilterBackend here we can override the filter_queryset method for custom filtering and ordering. 

- used this in class ProductListCreateView() as : filter_backends = [ProductFilters,] 


### Pagination 
* update REST_FRAMEWORK dictionary in settings.py 
- add DEFAULT_PAGINATION_CLASS with page size (number of entries/instances per page) 
- in all get api responses will have 3 new attributes, 
- `next` : next page url (same url with ?page=2)
- `previous` : previous page url 
- `count` : totla number of pages 
- the pagination applies after filter_queryset, on `final` queryset so we can use it with ordering and filtering 
* ProductListCreateView
- we can have view specific `page_size` we can do it like we have done in this view, by setting `pagination_class.page_size`
- we can allow client to specify size by defining `page_size_query_param` in our view, like pagination_class.page_size_query_param = 'size'
- if client calls /products?size=4  `page_size` will become 4, 
- add pagination_class.max_page_size = 100 so that client can't do something like `?size=10000000000`


### Viewsets ('controller')
- combine similar views in single class called ViewSet, combines same logic(dry princple)
- ***example we use same queryset for all CRUD Views of orders, with viewset we only need to define queryset once.***
- ViewSet provides methods, list(), create(), update(), delete(), retreive()
- We can use routers, we don't need to configure urls a lot.


### api/urls.py 
- add DefaultRouter 
- register with a `prefix` ("orders",in our case) and `viewset` ("OrderViewSet", in our case)
- registering will auto-create 2 routes to OrderViewSet : 
- "/orders/" : for list() and create()
- "/orders/<int:pk>" : for retreive(), update() and delete()

`OrderViewSet`
- ModelViewSet (inherits form CreteModelMixin, RetriveModelMixin,.. all mixins)
- for `/orders/` prefix we can see the list of orders and also the post form if we open in browser 'http://127.0.0.1:8000/api/orders/'

- we want order id only in list and not in creation form, since we use the same serializer for both. We can create UUID read only field in OrderSerializer with name `order_id`. Now since Post form in browsable api renders acc. to serialzier, we will not see `order_id` in post form. 

- with `/order/id` we can retreive, update and delete order with particular id 

- ***All generic View attributes and methods like `serializer_class, permission_classes,  get_queryset,etc.` are also available in ViewSets***



### api/serializers.py 
`OrderCreateSerializer()`
- When we want to create instance with help of nested serializer, can do that but `we can only create one instance of child(nested) serializer's model`. 

- example : OrderItem has foreign referencing Order model. OrderItem is child. If we want to create an Order along with ONE OrderItem, we can easily do it by using nested serializer for creation.

- But usually we want to create many children(OrderItem) along with the parent(Order) for doing it. 

- ` we have to overrided the create method in parent serializer` and set many = True in OrderItemCreateSerializer. In create method we get the validated data, for which the serializers are actually used for.

- similarly added update and setted items as required = False

### api/views.py 
`OrderViewSet()`
- we want to use different serializer in case of post, so overided get_serializer method.

- override `perform_create()`, to pass rquest.user directly to serializer, 
- ***serializer's create gets it in validated_data.***

- in /orders POST data we can now send : 
```
{
    "status": "Confirmed",
    "items": [
        {
            "product" : 1,
            "quantity": 3
        },
        {
            "product":4,
            "quantity": 3
        }
    ]
}
```


### settings.py 
`REST_FRAMEWORK dictionary` 
- added throttle settings
- allows us to send limit the number requests per user, anonymus and authenticated both     


### Secrety key 
In Django, the SECRET_KEY is essentially the "master password" for your web application. It is a unique string used to provide cryptographic signing (salting), ensuring that data generated by your server hasn't been tampered with by a user or a third party. Used in sessions, csrf, password reseting, etc. Never commit it.