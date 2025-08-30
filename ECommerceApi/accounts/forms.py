from django.contrib.auth.forms import UserCreationForm
from .models import User 

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # fields = UserCreationForm.Meta.fields + ('role',)
        fields = ('username', 'email', 'password1', 'password2')