from django.contrib.auth.forms import UsernameField
from django import forms
from django.contrib.auth import (
    authenticate, get_user_model,
)
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


UserModel = get_user_model()


class FaceAuthenticationForm(forms.Form):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    face_img = forms.ImageField(label="Face image", required=True)

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Reject if face image is missing
        if "face_img" not in self.request.FILES:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'face_img': "Face image is missing"}
            )

        # Reject if face image is not one of the allowed content types
        face_img = self.request.FILES["face_img"]
        if face_img.content_type not in {"image/jpeg", "image/png"}:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'face_img': "File format not recognized"}
            )

        # Reject large images
        if face_img.size > 1024 * 1024:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'face_img': "File too large"}
            )

        face_img = face_img.file

        if username is not None:
            self.user_cache = authenticate(self.request, username=username, password=password, face_img=face_img)
            if self.user_cache is None:
                # An authentication backend may reject inactive users. Check
                # if the user exists and is inactive, and raise the 'inactive'
                # error if so.
                try:
                    self.user_cache = UserModel._default_manager.get_by_natural_key(username)
                except UserModel.DoesNotExist:
                    pass
                else:
                    self.confirm_login_allowed(self.user_cache)
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
