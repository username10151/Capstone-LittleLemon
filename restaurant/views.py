# from django.http import HttpResponse
from django.shortcuts import render
from .forms import BookingForm
from .models import Menu
from django.core import serializers
from .models import Booking
from datetime import datetime, date as pydate
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})


def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
        reservation_slot = data.get('reservation_slot', None)
        if reservation_slot is None or reservation_slot == '':
            return JsonResponse({'error': 'Invalid reservation slot'}, status=400)

        exist = Booking.objects.filter(
            reservation_date=data.get('reservation_date'),
            reservation_slot=data.get('reservation_slot')
        ).exists()

        if not exist:
            booking = Booking(
                first_name=data.get('first_name'),
                reservation_date=data.get('reservation_date'),
                reservation_slot=data.get('reservation_slot')
            )
            booking.save()
        else:
            return JsonResponse({'error': 'Booking already exists'}, status=400)

    date_str = request.GET.get('date', str(pydate.today()))
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    formatted_date = date.strftime('%Y-%m-%d')

    bookings = Booking.objects.filter(reservation_date=formatted_date)
    booking_data = [{'first_name': booking.first_name, 'reservation_slot': booking.reservation_slot} for booking in bookings]
    return JsonResponse(booking_data, safe=False)