from django.contrib.auth.decorators import user_passes_test
def is_admin(user):
    return user.is_staff or user.is_superuser
admin_required = user_passes_test(is_admin, login_url="login")
