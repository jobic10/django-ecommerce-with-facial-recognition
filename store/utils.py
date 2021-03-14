from .models import Customer, Order


def return_session(request):
    """
    Small function that returns session_key, if session does not exists - creates it.
    :param request:
    :return: session_key
    """
    if request.session.exists(request.session.session_key):
        return request.session.session_key
    else:
        request.session.create()
        return request.session.session_key


def return_order_and_items(request):
    """
    This func takes request and returns for both auth and unauth users: customer, items, customer
    :param request:
    :return: Query obj (tuple)
    """
    order = None
    items = None
    customer = None
    if request.user.is_authenticated:
        customer = request.user.customer  # one to one relation
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()

    return order, items, customer
