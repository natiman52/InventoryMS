# Django core imports
from django.urls import path

# Local app imports
from .views import (
    MaterialListView,
    material_create_view,
    BillUpdateView,
    BillDeleteView,
    MaterialDetailView
)

# URL patterns
urlpatterns = [
    # Bill URLs
    path(
        'materials/',
        MaterialListView.as_view(),
        name='bill_list'
    ),
    path('materials/<str:id>',MaterialDetailView.as_view(),name='bill-detail'),
    path('new-materials/',material_create_view, name='bill_create'),
    path(
        'bill/<slug:slug>/update/',
        BillUpdateView.as_view(),
        name='bill_update'
    ),
    path(
        'bill/<slug:pk>/delete/',
        BillDeleteView.as_view(),
        name='bill_delete'
    ),
]
