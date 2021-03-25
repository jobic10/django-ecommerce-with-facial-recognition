from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import *
from django.http import JsonResponse
from .forms import ShippingForm, CreateUserForm, CustomerForm
from .utils import return_session, return_order_and_items
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .decorators import if_unauthenticated
from django.conf import settings
import os
# Start Of Libraries Used For Facial Recognition
import sys
import cv2
import numpy as np
from PIL import Image as Img

# Paystack
from pypaystack import Transaction as PayStack
transaction = PayStack(authorization_key=settings.PAYSTACK_KEY)

harcascadePath = os.path.join(
    settings.BASE_DIR, "haarcascade_frontalface_default.xml")


@login_required
def verify(request):
    # Verify a transaction given a reference code "refcode".
    ref = request.GET.get('reference', None)
    if ref is None:
        messages.error(
            request, "We could not find a reference for this transaction")
    response = transaction.verify(ref)
    dic = response[3]
    if dic['status'] == 'success':  # Payment Approved
        # Update The Models To The Payment And Save The Amount Paid
        # First, insert into Transaction
        paid = dic['amount'] / 100
        tran = Transaction.objects.create(
            ref=ref, customer=request.user.customer, amount=paid)
        try:
            order = Order.objects.get(
                customer=request.user.customer, transaction=None)
            order.transaction = tran
            order.paid = True
            order.complete = True
            order.save()
            messages.success(request, "Payment Completed. Thank you!")
        except:
            messages.error(request, "No Items In Cart")
    else:
        messages.error(request, "Transaction not approved!")
    return redirect(reverse('store'))


@login_required
def pay(request):
    # Charge a customer N100.
    id = (request.user.customer.id)
    # Track Image
    check = TRACK(id)
    order, items, customer = return_order_and_items(request)
    total = order.get_cart_total * 100
    if total < 10:
        messages.error(request, "Please, add items to cart")
        return redirect(reverse('store'))
    if check == 1:
        response = transaction.initialize(request.user.email, int(total))
        if response[0] == 200 or response[0] == '200':
            url = response[3]['authorization_url']
            try:
                return redirect(url)
            except:
                messages.error(request, "Please check your internet settings")
            # response = transaction.charge(request.user.email, url, int(total))
        else:
            messages.error(request, "Please connect to internet")
    elif check == -1:
        return render(request, 'store/login.html', {'error': 'Identity mismatch'})
    else:
        return render(request, 'store/login.html', {'error': 'Face not captured'})
    return redirect(reverse('store'))


def trainImage():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels(os.path.join(
        settings.BASE_DIR, "TrainingImages"))
    print("Faces = " + str(faces))
    print("At this point ID = ")
    print(Id)
    recognizer.train(faces, np.array(Id))
    recognizer.save(os.path.join(settings.BASE_DIR, "Trainer.yml"))


def takeImage(Id):
    broke = False
    if Id:
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0

        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # The last value here is the number of faces
            faces = detector.detectMultiScale(gray, 1.2, 2)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum = sampleNum + 1
                # store each customer picture with  username
                name = "file_" + str(Id) + '_' + str(sampleNum) + ".jpg"
                path = os.path.join(
                    settings.BASE_DIR, "TrainingImages", name)
                cv2.imwrite(path, gray[y:y + h, x:x + h])
                cv2.imshow('PLEASE, KEEP FACE STILL FOR RECOGNIZER', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                broke = True
                break
            # stop the camera when the number of picture exceed 50 pictures for each student
            if sampleNum > 50:
                break

        cam.release()
        cv2.destroyAllWindows()
        if broke:
            return None

        trainImage()
        return 1
    else:
        return None


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    Ids = []
    detector = cv2.CascadeClassifier(harcascadePath)
    for imagePath in imagePaths:
        pilImage = Img.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        print("Path = " + str(imagePath))
        Id = int(os.path.split(imagePath)[-1].split("_")[1])
        print("ID = " + str(Id))
        faces = detector.detectMultiScale(imageNp)
        faceSamples.append(imageNp)
        Ids.append(Id)
    print("###" * 40)
    print(faceSamples)
    print(Ids)
    print("###" * 40)
    return faceSamples, Ids


def store(request):
    order, items, customer = return_order_and_items(request)
    products = Product.objects.all()
    context = {'products': products, 'items': items, 'order': order}
    return render(request, 'store/store.html', context)


def cart(request):
    order, items, customer = return_order_and_items(request)
    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


@login_required
def checkout(request):
    instance = None

    shipping_form = ShippingForm(request.POST or None)
    order, items, customer = return_order_and_items(request)
    exist = ShippingAddress.objects.filter(
        customer=request.user.customer, order=order).exists()
    if exist:
        instance = ShippingAddress.objects.filter(
            customer=request.user.customer, order=order)[0]
        shipping_form = ShippingForm(request.POST or None, instance=instance)

    if order is None:
        messages.error(request, "Order cannot be empty")
        return redirect(reverse('store'))
    if request.method == 'POST':
        if order.shipping:
            if shipping_form.is_valid():
                ship = shipping_form.save(commit=False)
                ship.customer = request.user.customer
                ship.order = order
                ship.save()
                # Go to paystack
                return redirect(reverse('pay'))
            else:
                messages.error(request, "Invalid Form Submitted!")
        else:
            return redirect(reverse('pay'))

    context = {'items': items, 'order': order, 'shipping_form': shipping_form}
    return render(request, 'store/checkout.html', context)


@csrf_exempt
def update_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse(status=403, data={'error': 'You must be logged in!'})
    user = request.user
    customer = user.customer
    if request.POST:
        try:
            product_id = request.POST['id']
            action = request.POST['action']

            order, items, customer = return_order_and_items(request)

            try:
                product = Product.objects.get(id=product_id)
            except ObjectDoesNotExist:
                return JsonResponse(status=422, data={'error': 'You must provide valid id'})

            order_item, created = OrderItem.objects.get_or_create(customer=customer,
                                                                  order=order, product=product)

            if action == 'add':
                order_item.quantity += 1
            elif action == 'remove':
                order_item.quantity -= 1
            else:
                return JsonResponse(status=422, data={'error': 'You must provide valid action '})

            order_item.save()

            if order_item.quantity <= 0:
                order_item.delete()

            return JsonResponse('item added', safe=False)
        except KeyError:
            return JsonResponse(status=400, data={'error': 'You must provide id and action'})

    return JsonResponse(status=405, data={'error': 'You must provide post request'})


def validate_form(request):
    if request.method == "POST":
        form = ShippingForm(request.POST)

        order, items, customer = return_order_and_items(request)
        if order.shipping:
            if form.is_valid():
                address = request.POST.get('address')
                city = request.POST.get('city')
                phone = request.POST.get('phone')

                update = {'address': address, 'city': city, 'phone': phone}
                ShippingAddress.objects.update_or_create(
                    customer=customer, order=order, defaults=update)
                return JsonResponse('ok', safe=False, status=200)
            else:
                return JsonResponse(status=400, data={'error': 'You must provide shipping address'})

        return JsonResponse(status=200, data={'ok': 'ok'})

    return JsonResponse(status=405, data={'error': 'You must provide post request'})


def completed_order(request):
    """
    Future improvements: when payment methods are added, make query with paid=True, and change get_or_create on
    just get(). Moreover take transaction ID from payment widget and write it into DB.
    :param request:
    :return: render template
    """
    order, items, customer = return_order_and_items(request)
    # order.transaction_id = take_this_from_payment_response
    # order.complete = True
    # order.paid = True
    order.save()

    context = {'items': items, 'order': order}
    return render(request, 'store/order.html', context)


@login_required
def completed_orders(request):
    order, items, customer = return_order_and_items(request)
    orders = Order.objects.filter(customer=customer)
    context = {'items': items,
               'order': order, 'orders': orders}
    customer = request.user.customer
    return render(request, 'store/orders.html', context)


@login_required
def view_completed_orders(request, order_id):
    order, items, customer = return_order_and_items(request)
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    context = {'items': items,
               'order': order,  'order_items': order_items}
    return render(request, 'store/view_orders.html', context)


@if_unauthenticated
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            id = (user.customer.id)
            # Track Image
            check = TRACK(id)
            if check == 1:
                login(request, user)
                return redirect('store')
            elif check == -1:
                return render(request, 'store/login.html', {'error': 'Identity mismatch'})
            else:
                return render(request, 'store/login.html', {'error': 'Face not captured'})
        else:
            return render(request, 'store/login.html', {'error': 'Incorrect login/password, try again.'})

    context = {}
    return render(request, 'store/login.html', context)


def TRACK(phone):
    import os
    os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(settings.BASE_DIR, "Trainer.yml"))
    faceCascade = cv2.CascadeClassifier(harcascadePath)

    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    cv2.VideoCapture(0).release()
    cv2.destroyAllWindows()
    cam = cv2.VideoCapture(0)
    good = 0
    bad = 0
    value = 0
    while True:
        try:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 2)
            if value != 0:
                break
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x-20, y-20), (x+w+20, y+h+20),
                              (0, 255, 0), 4)  # Online
                Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                #  a confidence less than 50 indicates a good face recognition
                if conf < 50:  # Good one is 50
                    # Now, we count if this confidence is up to 5
                    if Id != phone:
                        bad = bad + 1
                        if bad > 5:
                            value = -1
                            break
                    else:
                        good = good + 1
                        if good > 5:
                            value = 1
                            break
                else:
                    bad = bad + 0.3
                    if bad > int(5):
                        value = -1
                        break
                    Id = 'Keep Head Still'
                    tt = str(Id)
                    #  store the unknown images in the images unknown folder
                    cv2.putText(img, str(tt), (x, y + h - 10),
                                font, 0.8, (255, 255, 255), 1)
                print("Bad = " + str(bad) + " while good is " + str(good))
                cv2.imshow(
                    'PLEASE KEEP HEAD STILL - LIKE YOU DID WHILE REGISTERING', img)
            if cv2.waitKey(1000) == ord('q'):
                value = -1
                break
        except:
            cam.release()
            cv2.destroyAllWindows()
            value = -1
            break
    cam.release()
    cv2.destroyAllWindows()
    return value


@if_unauthenticated
def registration_view(request):
    form = CreateUserForm(request.POST or None)
    form2 = CustomerForm(request.POST or None)
    context = {'form': form, 'form2': form2}
    if request.method == 'POST':
        if form.is_valid() and form2.is_valid():
            # Train Photo
            user = form.save()
            customer = form2.save(commit=False)
            customer.user = user
            customer.save()
            try:
                capture = takeImage(customer.id)
                if capture is None:
                    customer.delete()
                    user.delete()
                    messages.error(request, "We could not capture your face.")
                    return render(request, 'store/registration.html', context)
            except:
                customer.delete()
                user.delete()
                messages.error(request, "We could not capture your face.")
                return render(request, 'store/registration.html', context)
            messages.success(
                request, f'Account was created successfully, now you can log in.')
            return redirect('login')
        else:
            messages.error(request, "Invalid Form Submitted")

    return render(request, 'store/registration.html', context)


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')
