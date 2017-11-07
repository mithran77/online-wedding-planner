from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.template import Template , Context
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from paypal.standard.forms import PayPalPaymentsForm

from .models import Hall, Caterer, Florist, CatererBooking, HallBooking, FloristBooking
from .forms import SignUpForm, BookingHallForm, BookingCatererForm, BookingFloristForm


BOOKING_TITLE = '{} Booking Confirmation'
BOOKING_BODY = 'This is to confirm booking, {} in the {}'

def landing_page(request):
    return render(request, 'weddingServices/landing_page.html', {'post': ''})

def hall_list(request):
    halls = Hall.objects.order_by('added_date')
    return render(request, 'weddingServices/hall_list.html', {'halls': halls})

def caterer_list(request):
    caterers = Caterer.objects.order_by('added_date')
    return render(request, 'weddingServices/caterer_list.html', {'caterers': caterers})

def florist_list(request):
    florists = Florist.objects.order_by('added_date')
    return render(request, 'weddingServices/florist_list.html', {'florists': florists})

def hall_detail(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    return render(request, 'weddingServices/hall_detail.html', {'hall': hall})

def caterer_detail(request, pk):
    caterer = get_object_or_404(Caterer, pk=pk)
    return render(request, 'weddingServices/caterer_detail.html', {'caterer': caterer})

def florist_detail(request, pk):
    florist = get_object_or_404(Florist, pk=pk)
    return render(request, 'weddingServices/florist_detail.html', {'florist': florist})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/weddingServices/')
    else:
        form = SignUpForm()
    return render(request, 'weddingServices/sign_up.html', {'form': form})

def bookdate_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        form = BookingHallForm(request.POST, pk=pk)
        try:
            form.is_valid()
        except AttributeError:
            pass		

        if form.is_valid():
            obj = HallBooking()
            obj.booking_date = form.cleaned_data.get('booking_date')
            obj.time_slots = form.cleaned_data.get('time_slots')
            obj.hall_id = int(pk)
            obj.user = request.user
            obj.cost = Hall.objects.get(pk=obj.hall_id).session_cost * len(obj.time_slots)
            obj.save()
			# Send email
            email = EmailMessage(
                BOOKING_TITLE.format('Caterer'),
                BOOKING_BODY.format(obj.booking_date, obj.time_slots),
                to=[obj.user.email, Caterer.objects.get(pk=int(pk)).email])
            email.send()
            #import ipdb; ipdb.set_trace()
            return redirect('bookdate/' + str(obj.pk) + '/payment')
    else:
        form = BookingHallForm()
        #import ipdb; ipdb.set_trace()
    return render(request, 'weddingServices/book_date.html', {'form': form})


def bookdate_caterer(request, pk):
    caterer = get_object_or_404(Caterer, pk=pk)

    if request.method == 'POST':
        form = BookingCatererForm(request.POST, pk=pk)
        try:
            form.is_valid()
        except AttributeError:
            pass

        if form.is_valid():
            obj = CatererBooking()
            #import ipdb; ipdb.set_trace()
            obj.booking_date = form.cleaned_data.get('booking_date')
            obj.time_slots = form.cleaned_data.get('time_slots')
            obj.caterer_id = int(pk)
            obj.user = request.user
            obj.cost = Caterer.objects.get(pk=obj.caterer_id).session_cost * len(obj.time_slots)
            obj.save()
			# Send email
            email = EmailMessage(
                BOOKING_TITLE.format('Caterer'),
                BOOKING_BODY.format(obj.booking_date, obj.time_slots),
                to=[obj.user.email, Caterer.objects.get(pk=int(pk)).email])
            email.send()
            #import ipdb; ipdb.set_trace()
            return redirect('bookdate/' + str(obj.pk) + '/payment')
    else:
        form = BookingCatererForm()
        #import ipdb; ipdb.set_trace()
    return render(request, 'weddingServices/book_date.html', {'form': form})

def bookdate_florist(request, pk):
    florist = get_object_or_404(Florist, pk=pk)
    if request.method == 'POST':
        form = BookingFloristForm(request.POST, pk=pk)

        try:
            form.is_valid()
        except AttributeError:
            pass

        if form.is_valid():
            obj = FloristBooking()
            obj.booking_date = form.cleaned_data.get('booking_date')
            obj.time_slots = form.cleaned_data.get('time_slots')
            obj.florist_id = int(pk)
            obj.user = request.user
            obj.cost = Florist.objects.get(pk=obj.florist_id).session_cost * len(obj.time_slots)
            obj.save()
			# Send email
            email = EmailMessage(
                BOOKING_TITLE.format('Caterer'),
                BOOKING_BODY.format(obj.booking_date, obj.time_slots),
                to=[obj.user.email, Caterer.objects.get(pk=int(pk)).email])
            email.send()
            #import ipdb; ipdb.set_trace()
            return redirect('bookdate/' + str(obj.pk) + '/payment')

    else:
        form = BookingFloristForm()
        #import ipdb; ipdb.set_trace()
    return render(request, 'weddingServices/book_date.html', {'form': form})

def payment_hall(request, pk):
    hall_payment = get_object_or_404(HallBooking, pk=pk)
    #import ipdb; ipdb.set_trace()
    paypal_dict = {
        "business": User.objects.get(id=hall_payment.user_id).email,
        "amount": str(hall_payment.cost),
        "item_name": "payment for " + Hall.objects.get(id=hall_payment.hall_id).shop_name,
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('landing_page')),
        "cancel_return": request.build_absolute_uri(reverse('landing_page')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
   	}

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "weddingServices/payment_page.html", context)
	
def payment_caterer(request, pk):
    caterer_payment = get_object_or_404(CatererBooking, pk=pk)
    #import ipdb; ipdb.set_trace()
    paypal_dict = {
        "business": User.objects.get(id=caterer_payment.user_id).email,
        "amount": str(caterer_payment.cost),
        "item_name": "payment for " + Caterer.objects.get(id=caterer_payment.caterer_id).shop_name,
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('landing_page')),
        "cancel_return": request.build_absolute_uri(reverse('landing_page')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
   	}

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "weddingServices/payment_page.html", context)


def payment_florist(request, pk):
    florist_payment = get_object_or_404(FloristBooking, pk=pk)
    #import ipdb; ipdb.set_trace()
    paypal_dict = {
        "business": User.objects.get(id=florist_payment.user_id).email,
        "amount": str(florist_payment.cost),
        "item_name": "payment for " + Florist.objects.get(id=florist_payment.florist_id).shop_name,
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('landing_page')),
        "cancel_return": request.build_absolute_uri(reverse('landing_page')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
   	}

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "weddingServices/payment_page.html", context)