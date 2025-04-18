from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import Notification

class ComponentType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ComponentModel(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    class Meta:
        ordering = ['brand__name', 'name']

class Component(models.Model):
    type = models.ForeignKey(ComponentType, on_delete=models.CASCADE, related_name='components')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='components')
    model = models.ForeignKey(ComponentModel, on_delete=models.CASCADE, related_name='components')
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    specifications = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    stock_threshold = models.PositiveIntegerField(default=5, help_text="Minimum stock level before triggering alerts")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_components')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['type__name', 'brand__name', 'name']

    def save(self, *args, **kwargs):
        # Generate code if not provided
        if not self.code:
            prefix = f"{self.type.name[:3]}{self.brand.name[:3]}".upper()
            last_component = Component.objects.filter(code__startswith=prefix).order_by('-code').first()
            if last_component:
                try:
                    number = int(last_component.code[6:]) + 1
                except ValueError:
                    number = 1
            else:
                number = 1
            self.code = f"{prefix}{number:04d}"

        # Check if stock falls below threshold
        if self.stock <= self.stock_threshold:
            # Notify supervisors about low stock
            supervisors = User.objects.filter(is_staff=True)
            for supervisor in supervisors:
                Notification.send_notification(
                    recipient=supervisor,
                    title='Low Stock Alert',
                    message=f'Low stock alert: {self.name} ({self.stock} remaining)',
                    level='warning',
                    related_object_type='Component',
                    related_object_id=self.id
                )

        super().save(*args, **kwargs)

class ComponentCompatibility(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='compatibility_as_primary')
    compatible_with = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='compatibility_as_secondary')
    notes = models.TextField(blank=True, help_text="Additional compatibility information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.component == self.compatible_with:
            raise ValidationError("A component cannot be compatible with itself.")
        if self.component.type == self.compatible_with.type:
            raise ValidationError("Cannot set compatibility between components of the same type.")

    def __str__(self):
        return f"{self.component.name} ↔ {self.compatible_with.name}"

    class Meta:
        unique_together = ['component', 'compatible_with']
        verbose_name_plural = 'Component compatibilities'

    @classmethod
    def check_compatibility(cls, components):
        """
        Check if a list of components are compatible with each other.
        Returns (is_compatible, issues)
        """
        issues = []
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                if comp1.type == comp2.type:
                    issues.append(f"Duplicate component type: {comp1.type.name}")
                    continue
                
                compatibility = cls.objects.filter(
                    models.Q(component=comp1, compatible_with=comp2) |
                    models.Q(component=comp2, compatible_with=comp1)
                ).first()
                
                if not compatibility:
                    issues.append(f"No compatibility data for {comp1.name} and {comp2.name}")
        
        return len(issues) == 0, issues
