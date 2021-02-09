from datetime import datetime, timezone


def user_details(strategy, details, backend, user=None, *args, **kwargs):
    """
    This is modified version of: `social_core.pipeline.user.user_details`.
    We don't want social_auth to update `first_name` and `last_name` everytime we loggedin
    but only the first time we login/register.
    """
    if not user:
        return
    changed = False  # flag to track changes

    # if date_joined is less than 10 seconds ago, allow overrides the details
    # otherwise ignore details changes.
    now = datetime.now(timezone.utc)
    diff = now - user.date_joined
    if diff.seconds > 10:
        return

    # Default protected user fields (username, id, pk and email) can be ignored
    # by setting the SOCIAL_AUTH_NO_DEFAULT_PROTECTED_USER_FIELDS to True
    if strategy.setting('NO_DEFAULT_PROTECTED_USER_FIELDS') is True:
        protected = ()
    else:
        protected = ('username', 'id', 'pk', 'email', 'password',
                     'is_active', 'is_staff', 'is_superuser',)

    protected = protected + \
        tuple(strategy.setting('PROTECTED_USER_FIELDS', []))

    # Update user model attributes with the new data sent by the current
    # provider. Update on some attributes is disabled by default, for
    # example username and id fields. It's also possible to disable update
    # on fields defined in SOCIAL_AUTH_PROTECTED_USER_FIELDS.
    field_mapping = strategy.setting('USER_FIELD_MAPPING', {}, backend)
    for name, value in details.items():
        # Convert to existing user field if mapping exists
        name = field_mapping.get(name, name)
        if value is None or not hasattr(user, name) or name in protected:
            continue

        current_value = getattr(user, name, None)
        if current_value == value:
            continue

        changed = True
        setattr(user, name, value)

    if changed:
        strategy.storage.user.changed(user)
