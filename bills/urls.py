# Django core imports
from django.urls import path

# Local app imports
from .views import (
    MaterialListView,
    material_create_view,
    BillUpdateView,
    BillDeleteView,
    MaterialDetailView,
    BillListView,
    ClientPaymentListCreate,
    EmployeePayroll,
    BillCreateView,
    daily_activity
)

# URL patterns
urlpatterns = [
    path(
        'materials/',
        MaterialListView.as_view(),
        name='bill_list'
    ),
    path('materials/<str:id>',MaterialDetailView.as_view(),name='bill-detail'),
    path('new-materials/',material_create_view, name='material_create'),
    path("",BillListView.as_view(),name='expanse_list'),
    path("create/",BillCreateView.as_view(),name='bill_create'),
    path(
        '<slug:slug>/update/',
        BillUpdateView.as_view(),
        name='bill_update'
    ),
    path(
        '<slug:pk>/delete/',
        BillDeleteView.as_view(),
        name='bill_delete'
    ),
    path('client/<int:id>',ClientPaymentListCreate.as_view(),name="client_payment_list_create"),
    path('employee/<int:id>',EmployeePayroll.as_view(),name="payroll"),
    path('daily_activity',daily_activity,name='daily')
]
