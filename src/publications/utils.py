from django.conf import settings


def check_publication_management_user(user):
    return not user.is_anonymous and user.user_id in settings.PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS
