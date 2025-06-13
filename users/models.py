
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.conf import settings
import os


def temp_directory_path(instance, filename):
    """Save files temporarily in a 'temp' folder."""
    ext = filename.split('.')[-1]
    return f"temp/{filename.split('.')[0]}.{ext}"


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role_id}"


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    roles = models.ManyToManyField('Role')
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to=temp_directory_path, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)
    #status = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100,default='inactive')
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    pan = models.FileField(upload_to=temp_directory_path, blank=True, null=True)
    aadhaar = models.FileField(upload_to=temp_directory_path, blank=True, null=True)
    kyc_status = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    account_type = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=60, blank=True, null=True)
    nominee_reference_to = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    referral_id = models.CharField(max_length=20, blank=True, null=True)
    referred_by = models.CharField(max_length=20, blank=True, null=True)
    # level_no = models.CharField(max_length=20, blank=True, null=True)
    level_no = models.PositiveIntegerField(default=0)



    

    def set_roles(self, roles):
        """Temporarily store roles to set after save."""
        self._roles_data = roles

    def save(self, *args, **kwargs):
        new_user = not self.pk
        # Set level_no based on referred_by
        if self.referred_by:
            try:
                referring_user = User.objects.get(referral_id=self.referred_by)
                self.level_no = (referring_user.level_no or 0) + 1
            except User.DoesNotExist:
                self.level_no = 0
        else:
            self.level_no = 0

        # Handle file cleanup if updating
        if self.pk:
            existing_user = User.objects.get(pk=self.pk)
            for file_field in ['image', 'pan', 'aadhaar']:
                new_file = getattr(self, file_field)
                old_file = getattr(existing_user, file_field)
                if new_file and old_file and old_file.name != new_file.name:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, old_file.name)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

        # Hash password if not already hashed
        if self.pk:
            existing_user = User.objects.get(pk=self.pk)
            if self.password != existing_user.password and not self.password.startswith('pbkdf2_sha256$'):
                self.password = make_password(self.password)
        else:
            if not self.password.startswith('pbkdf2_sha256$'):
                self.password = make_password(self.password)

        super().save(*args, **kwargs)

        # Move files to user folder
        self.move_files_to_user_folder()

        # Assign roles if provided
        if hasattr(self, '_roles_data'):
            self.roles.set(self._roles_data)

        

    def move_files_to_user_folder(self):
        """Move files from temp folder to user_id folder after user creation."""
        for file_field in ['image', 'pan', 'aadhaar']:
            file_instance = getattr(self, file_field)
            if file_instance:
                old_path = file_instance.name
                ext = old_path.split('.')[-1]
                new_path = f"{self.user_id}/{file_field}.{ext}"
                if old_path.startswith("temp/") and old_path != new_path:
                    with default_storage.open(old_path, 'rb') as file_content:
                        default_storage.save(new_path, ContentFile(file_content.read()))
                    default_storage.delete(old_path)
                    setattr(self, file_field, new_path)
                    super().save(update_fields=[file_field])

    def delete(self, *args, **kwargs):
        """Delete the user's folder and all files inside it when the user is deleted."""
        user_folder = os.path.join(settings.MEDIA_ROOT, str(self.user_id))
        if os.path.exists(user_folder) and os.path.isdir(user_folder):
            for file_name in os.listdir(user_folder):
                file_path = os.path.join(user_folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(user_folder)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id}"
    






class MeetingRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_requests')
    referral_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    profile_type = models.CharField(max_length=200)
    requested_date = models.DateField()
    requested_time = models.TimeField()
    #message = models.TextField(blank=True, null=True)
    is_scheduled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} → {self.profile_type} on {self.requested_date}"

# class ScheduledMeeting(models.Model):
#     scheduled_meeting_id = models.AutoField(primary_key=True)
#     request = models.OneToOneField(MeetingRequest, on_delete=models.CASCADE)
#     scheduled_date = models.DateField(blank=True, null=True)
#     scheduled_time = models.TimeField(blank=True, null=True)
#     meeting_link = models.URLField(blank=True, null=True)
#     scheduled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scheduled_meetings')
#     status_choices = [
#         ('scheduled', 'Scheduled'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled')
#     ]
#     status = models.CharField(max_length=20, choices=status_choices)
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.request.user_id} with {self.request.profile_type} on {self.scheduled_date}"

class ScheduledMeeting(models.Model):
    scheduled_meeting_id = models.AutoField(primary_key=True)
    request = models.OneToOneField(MeetingRequest, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_scheduled_meetings',blank=True, null=True)
    referral_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_type = models.CharField(max_length=200,blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    scheduled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scheduled_meetings')
    status_choices = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    notes = models.TextField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False,blank=True, null=True)

    def __str__(self):
        return f"{self.request.user_id} with {self.request.profile_type} on {self.scheduled_date}"





