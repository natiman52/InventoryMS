# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
# Local app imports
from . import views2
from . import views
from .views import (
    ProductListView,
    ProductDetailView,
    ProductDeleteView,
    ItemSearchListView,
    DeliveryListView,
    DeliveryDetailView,
    DeliveryCreateView,
    DeliveryUpdateView,
    DeliveryDeleteView,
    get_items_ajax_view,
    Item_create_view,
    DXFUpdateView,
    PhotoCreateView,
    DXFCreateView,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    GivenOrderListView,
    Dashboard,
    AllList,
    HomePage
)

# URL patterns
urlpatterns = [
    path('qoutes',views2.showQoutes,name="qoute_list"),
    # Dashboard
    path("",HomePage,name="home"),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('all_list',AllList.as_view(),name="all_list"),
    # Product URLs
    path('order-list/',ProductListView.as_view(),name='order-lists'),
    path('given-order/',GivenOrderListView.as_view(),name="given-order"),
    path('order/<str:type>',views.listofOrders,name='order-type'),
    path('order/<str:type>/photos',views.listofPhoto,name='order-photo'),
    path('order/<str:type>/dxf',views.listofDxf,name='order-dxf'),
    path('new-order/<str:id>/', ProductDetailView.as_view(), name='product-detail'),
    path( 'create/new-order/<str:type>', Item_create_view,name='product-create'),
    path('create/new-photo/<str:type>',PhotoCreateView.as_view(),name="photo-create"),
    path('create/new-dxf/<str:type>',DXFCreateView.as_view(),name="dxf-create"),
    path('product/<slug:slug>/delete/',ProductDeleteView.as_view(),name='product-delete'),
    path('update/new-dxf/<int:id>',DXFUpdateView.as_view(),name="dxf-update"),
    
    # Designner 
    path("designer-order/<str:id>",views2.design_detail_view,name='designer-order'),
    path('designer-order-list/',views2.DesignerOrderList.as_view(),name='designer-order-list'),
    path("designer-order-finished/",views2.DesignerOrderListFinished.as_view(),name="designer-order-finished"),
    
    # Accountant

    #operator
    path('operator-finished/',views2.OperatorFinishedList.as_view(),name='operator-finished'),
    path('operator-detail/<str:id>',views2.operator_detail_view,name='operator-detail'),

    # Item search
    path(
        'search/',
        ItemSearchListView.as_view(),
        name='item_search_list_view'
    ),

    # Delivery URLs
    path(
        'deliveries/',
        DeliveryListView.as_view(),
        name='deliveries'
    ),
    path(
        'delivery/<slug:slug>/',
        DeliveryDetailView.as_view(),
        name='delivery-detail'
    ),
    path(
        'new-delivery/',
        DeliveryCreateView.as_view(),
        name='delivery-create'
    ),
    path(
        'delivery/<int:pk>/update/',
        DeliveryUpdateView.as_view(),
        name='delivery-update'
    ),
    path(
        'delivery/<int:pk>/delete/',
        DeliveryDeleteView.as_view(),
        name='delivery-delete'
    ),

    # AJAX view
    path(
        'get-items/',
        get_items_ajax_view,
        name='get_items'
    ),

    # Category URLs
    path(
        'categories/',
        CategoryListView.as_view(),
        name='category-list'
    ),
    path(
        'categories/<int:pk>/',
        CategoryDetailView.as_view(),
        name='category-detail'
    ),
    path(
        'categories/create/',
        CategoryCreateView.as_view(),
        name='category-create'
    ),
    path(
        'categories/<int:pk>/update/',
        CategoryUpdateView.as_view(),
        name='category-update'
    ),
    path(
        'categories/<int:pk>/delete/',
        CategoryDeleteView.as_view(),
        name='category-delete'
    ),
    path('quote',views2.createQuote,name="create_quote"),
    path('quote/delete/<int:id>',views2.deleteQuote,name='quote-delete'),
    path('quote/send-email/<int:id>',views2.sendQuoteEmail,name='send-quote-email')
]

# Static media files configuration for development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
