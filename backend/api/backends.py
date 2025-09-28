# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend
#
# User = get_user_model()
#
#
# class EmailOrUsernameModelBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         if username is None:
#             username = kwargs.get(User.USERNAME_FIELD)
#
#         if '@' in username:
#             kwargs = {'email__iexact': username}
#         else:
#             kwargs = {'username__iexact': username}
#
#         try:
#             user = User.objects.filter(**kwargs).first()
#             if user and user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None
#         return None