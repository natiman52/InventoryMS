# Django core imports
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

# Local app imports
from accounts import views as user_views
from .views import (
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
    get_customers,
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
    SupplierSellsListView,
)

urlpatterns = [
    # User authentication URLs
    path('register/', user_views.register, name='user-register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'), name='user-login'),
    path('profile/', user_views.profile, name='user-profile'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='accounts/logout.html'), name='user-logout'),
     path('changepassword/',user_views.changepassword, name='user-changepassword'),
    # Customer URLs
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', CustomerCreateView.as_view(),
         name='customer_create'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(),
         name='customer_update'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(),
         name='customer_delete'),
    path('get_customers/', get_customers, name='get_customers'),
    #accounts
    path('account-order-list/',user_views.AccountOrderList.as_view(),name="account-order-list"),
    path("account-order/<str:id>",user_views.AccountDetailView.as_view(),name='account-order'),
    path("account-order-finished/",user_views.AccountOrderListFinished.as_view(),name="account-order-finished"),
    path("account-customer-order/<int:id>",user_views.AccountCustomerOrderList.as_view(),name="account-customer-order"),
    #overtime
    path("overtime",user_views.OverTimeDisplayView.as_view(),name="my-overtime"),
    path("overtimedetail/<int:id>",user_views.OverTimeDetailView.as_view(),name="overtime-detail"),
    path('all-overtimes',user_views.AllOverTimeDisplay.as_view(),name='all-overtime'),

    # Vendor URLs
    path('supplier/', SupplierListView.as_view(), name='vendor-list'),
    path('supplier/new/', SupplierCreateView.as_view(), name='vendor-create'),
    path('supplier/<int:id>/supplied',SupplierSellsListView.as_view(),name="supplies-sells"),
    path('supplier/<int:pk>/update/', SupplierUpdateView.as_view(),
         name='vendor-update'),
    path('supplier/<int:pk>/delete/', SupplierDeleteView.as_view(),
         name='vendor-delete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
