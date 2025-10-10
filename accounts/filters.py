import django_filters
from .models import MyUser


class StaffFilter(django_filters.FilterSet):
    """Filter set for the Profile model to refine staff searches."""

    class Meta:
        """Meta options for the StaffFilter."""
        model = MyUser
        fields = ['user', 'email', 'role', 'status']
