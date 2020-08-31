
def issue_signup_point(user=None, *args, **kwargs):
    from currencies import tasks

    if user is None:
        return
    tasks.issue_signup_point(user)
