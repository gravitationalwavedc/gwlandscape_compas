from functools import wraps
from graphene import ResolveInfo

# These are essentially the decorators that grpahql_jwt provides for us,
# but since we no longer use that package we need to provide them ourselves


class PermissionDenied(Exception):
    default_message = "You do not have permission to perform this action"

    def __init__(self, message=None):
        if message is None:
            message = self.default_message

        super().__init__(message)


def context(f):
    def decorator(func):
        def wrapper(*args, **kwargs):
            info = next(arg for arg in args if isinstance(arg, ResolveInfo))
            return func(info.context, *args, **kwargs)

        return wrapper

    return decorator


def user_passes_test(test_func, exc=PermissionDenied):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if test_func(context.user):
                return f(*args, **kwargs)
            raise exc

        return wrapper

    return decorator


login_required = user_passes_test(lambda u: u.is_authenticated)
staff_member_required = user_passes_test(lambda u: u.is_staff)
superuser_required = user_passes_test(lambda u: u.is_superuser)
