from django.shortcuts import redirect


def if_unauthenticated(view_func):
    """
    Redirect auth users from pointed page to store page.
    :param view_func:
    :return:
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper





