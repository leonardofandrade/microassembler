from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from supervisor.models import Component, ComponentCompatibility
from core.models import Notification

class AssemblyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assembly_requests')
    deadline = models.DateTimeField()
    observations = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_requests'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_assembly_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    compatibility_issues = models.TextField(blank=True, help_text="Any compatibility issues found during validation")

    def __str__(self):
        return f"Request #{self.id} by {self.customer.username}"

    def clean(self):
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError({'deadline': 'Deadline must be in the future.'})
        
        # Check component compatibility
        components = [rc.component for rc in self.components.all()]
        if components:
            is_compatible, issues = ComponentCompatibility.check_compatibility(components)
            if not is_compatible:
                self.compatibility_issues = "\n".join(issues)
                # Don't raise validation error, just store the issues for review

    def save(self, *args, **kwargs):
        # If this is a new request
        if not self.pk:
            super().save(*args, **kwargs)
            # Notify supervisors about new request
            supervisors = User.objects.filter(is_staff=True)
            for supervisor in supervisors:
                Notification.send_notification(
                    recipient=supervisor,
                    title='New Assembly Request',
                    message=f'New assembly request #{self.id} created by {self.customer.username}',
                    level='info',
                    related_object_type='AssemblyRequest',
                    related_object_id=self.id,
                    sender=self.customer
                )
        else:
            # If status changed to approved/rejected, set reviewed info
            if 'status' in kwargs.get('update_fields', []):
                if self.status in ['approved', 'rejected']:
                    self.reviewed_at = timezone.now()
            
            # If assigned_to changed, notify the assembler
            if self.assigned_to and self.assigned_to_id != self._state.fields_cache.get('assigned_to_id'):
                self.assigned_at = timezone.now()
                Notification.send_notification(
                    recipient=self.assigned_to,
                    title='Assembly Request Assigned',
                    message=f'Assembly request #{self.id} has been assigned to you',
                    level='info',
                    related_object_type='AssemblyRequest',
                    related_object_id=self.id,
                    sender=self.reviewed_by or self.customer
                )
            
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class RequestComponent(models.Model):
    request = models.ForeignKey(AssemblyRequest, on_delete=models.CASCADE, related_name='components')
    component = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='request_components')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.component.name} x{self.quantity} for Request #{self.request.id}"

    def clean(self):
        if self.quantity > self.component.stock:
            raise ValidationError({
                'quantity': f'Not enough stock. Available: {self.component.stock}'
            })

        # Check if adding this component would create compatibility issues
        current_components = [rc.component for rc in self.request.components.exclude(id=self.id)]
        current_components.append(self.component)
        is_compatible, issues = ComponentCompatibility.check_compatibility(current_components)
        if not is_compatible:
            raise ValidationError({
                'component': f'Compatibility issues found: {", ".join(issues)}'
            })

    class Meta:
        unique_together = ['request', 'component']
        ordering = ['component__type__name', 'component__name']

class AssemblyProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('issues', 'Issues Found')
    ]

    request = models.ForeignKey(AssemblyRequest, on_delete=models.CASCADE, related_name='progress_updates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    expected_completion = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Progress for Request #{self.request.id}: {self.status}"

    def save(self, *args, **kwargs):
        # If status changed to in_progress and started_at not set
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
        
        # If status changed to completed and completed_at not set
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Update parent request status
        if self.status == 'completed':
            self.request.status = 'completed'
            self.request.save(update_fields=['status'])
        elif self.status == 'in_progress':
            self.request.status = 'in_progress'
            self.request.save(update_fields=['status'])

        # Notify customer about status change
        if self.pk:  # If this is an update
            old_instance = AssemblyProgress.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                Notification.send_notification(
                    recipient=self.request.customer,
                    title='Assembly Status Update',
                    message=f'Assembly status updated to {self.get_status_display()}',
                    level='info',
                    related_object_type='AssemblyProgress',
                    related_object_id=self.id,
                    sender=self.updated_by
                )

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
