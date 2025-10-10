# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local app imports
from .views import (
    InvoiceListView,
    InvoiceDetailView,
    InvoiceCreateView,
    InvoiceUpdateView,
    InvoiceDeleteView,
    InvoicePrepView,
    create_operation_cost,
)

# URL patterns
urlpatterns = [
    # Invoice URLs
    path(
        'audit-history/',
        InvoiceListView.as_view(),
        name='invoicelist'
    ),
    path('create_operation',create_operation_cost,name='create_operation_cost'),
    path("prep-audit/",InvoicePrepView.as_view(),name="invoiceprep"),
    path(
        'audit/<int:id>/',
        InvoiceDetailView.as_view(),
        name='invoice-detail'
    ),
    path(
        'new-audit/<str:id>',
        InvoiceCreateView.as_view(),
        name='invoice-create'
    ),
    path(
        'audit/<slug:slug>/update/',
        InvoiceUpdateView.as_view(),
        name='invoice-update'
    ),
    path(
        'audit/<int:pk>/delete/',
        InvoiceDeleteView.as_view(),
        name='invoice-delete'
    ),
]

# Static media files configuration for development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
