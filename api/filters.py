

from rest_framework import filters

class ProductFilters(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(stock__gt=0)
        price = request.query_params.get('price')
        if price is not None:
                return queryset.filter(price__lte=price)
        return queryset

class OrderFilters(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
            return queryset.exclude(status='Cancelled')
    
    