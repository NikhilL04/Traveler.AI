from django.shortcuts import render
from travelapp.models import Destinations
from django.core.paginator import Paginator

# importing render and redirect
from django.shortcuts import render, redirect
# importing the openai API
import openai
from django.core.mail import send_mail
from gtts import gTTS
import os
from .models import Destinations,Verify,SignUp
from .forms import DestForm,VerForm
# import the generated API key from the secret_key file
from .secret_key import API_KEY
# loading the API key from the secret_key file
openai.api_key = API_KEY
import requests
import pytz
# Create your views here.

def home_page(request):
        try:
            data = Destinations.objects.all()

        except Destinations.DoesNotExist:

            data = None

        return render(request, 'travelapp/home.html', {'data': data})

def get_Destinations(request):
    user_dest = request.GET.get('near_city', '')

    try:
        data = Destinations.objects.filter(near_city=user_dest)
        weather_data = get_weather(request, user_dest)

    except Destinations.DoesNotExist:

        data = None

    return render(request, 'travelapp/home.html', {'data': data})

from django.shortcuts import render
from rest_framework.decorators import api_view
import json
import urllib.request

@api_view(['GET'])
def get_weather(request, city):
    api_key = '#'

    if not city:
        return render(request, 'travelapp/error.html', {'error': 'City not provided'})

    try:
        # Fetch current weather data
        current_source = urllib.request.urlopen(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        ).read()

        # Parse current weather JSON data
        current_data = json.loads(current_source)

        # Fetch forecast data
        forecast_source = urllib.request.urlopen(
            f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
        ).read()

        # Parse forecast JSON data
        forecast_data = json.loads(forecast_source)

        # Extract relevant current weather information
        data = {
            "country_code": str(current_data['sys']['country']),
            "coordinate": str(current_data['coord']['lon']) + ' ' + str(current_data['coord']['lat']),
            "temp": str(current_data['main']['temp']) + '°C',
            "pressure": str(current_data['main']['pressure']),
            "humidity": str(current_data['main']['humidity']),
            "cloudiness": str(current_data['clouds']['all']) + '%',
            "visibility": str(round(float(current_data['visibility']) / 1000, 2)) + ' km',  # Convert to km
            "wind_speed": str(round(float(current_data['wind']['speed']) * 3.6, 2)) + ' km/h',  # Convert to km/h
            "precipitation": 'Yes' if any(condition in current_data['weather'][0]['description'].lower() for condition in ['rain', 'drizzle', 'snow']) else 'No',
        }

        # Extract relevant forecast information for the next few days
        forecast = []
        for entry in forecast_data['list']:
            forecast.append({
                "date": entry['dt_txt'],
                "temp": str(entry['main']['temp']) + '°C',
                "humidity": str(entry['main']['humidity']),
                "cloudiness": str(entry['clouds']['all']) + '%',
                "wind_speed": str(round(float(entry['wind']['speed']) * 3.6, 2)),  # Convert to km/h
                "precipitation": 'Yes' if any(condition in entry['weather'][0]['description'].lower() for condition in ['rain', 'drizzle', 'snow']) else 'No',
            })

        return render(request, 'travelapp/weather.html', {'data': data, 'forecast': forecast})
    except Exception as e:
        return render(request, 'travelapp/error.html', {'error': f'Error fetching weather data: {str(e)}'})

from datetime import datetime

@api_view(['GET'])
def getcurrent_weather(request, city):
    api_key = "#"  # Remember to replace this with your actual API key

    if not city:
        return render(request, 'travelapp/error.html', {'error': 'City not provided'})

    try:
        # Fetch current weather data
        current_source = urllib.request.urlopen(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        ).read()

        # Parse current weather JSON data
        current_data = json.loads(current_source)
        precipitation_percentage = current_data['rain']['1h'] if 'rain' in current_data else 0
        utc_now = datetime.utcnow()

# Convert UTC time to Indian Standard Time (IST)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

# Format the time string

        # Extract relevant current weather information
        current_weather = {
            "city":city,
            "time": ist_now.strftime('%Y-%m-%d %H:%M:%S IST'),
            "temp": str(current_data['main']['temp']) + '°C',
            "humidity": str(current_data['main']['humidity']) + '%',
            "wind_speed": str(round(float(current_data['wind']['speed']) * 3.6, 2)),
             "precipitation": 'Yes' if any(condition in current_data['weather'][0]['description'].lower() for condition in ['rain', 'drizzle', 'snow']) else 'No',
            "cloudiness": str(current_data['clouds']['all']) + '%',
        }

        return render(request, 'travelapp/currentweather.html', {'current_weather': current_weather})
    except Exception as e:
        return render(request, 'travelapp/error.html', {'error': f'Error fetching weather data: {str(e)}'})

def travelAi(request):
    try:
        # if the session does not have a messages key, create one
        if 'messages' not in request.session:
            request.session['messages'] = [
                {"role": "system", "content": "You are now chatting with traveler.AI you can ask me question i will provide you short and concise answers."},
            ]
        if request.method == 'POST':
            # get the prompt from the form
            prompt = request.POST.get('prompt')
            # get the temperature from the form
            temperature = float(request.POST.get('temperature', 0.1))
            # append the prompt to the messages list
            request.session['messages'].append({"role": "user", "content": prompt})
            # set the session as modified
            request.session.modified = True
            # call the openai API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=request.session['messages'],
                temperature=temperature,
                max_tokens=1000,
            )
            # format the response
            formatted_response = response['choices'][0]['message']['content']
            # append the response to the messages list
            request.session['messages'].append({"role": "assistant", "content": formatted_response})
            request.session.modified = True
            # redirect to the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'temperature': temperature,
            }
            return render(request, 'travelapp/travelAi.html', context)
        else:
            # if the request is not a POST request, render the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'temperature': 0.1,
            }
            return render(request, 'travelapp/travelAi.html', context)
    except Exception as e:
        print(e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')

def new_chat(request):
    # clear the messages list
    request.session.pop('messages', None)
    return redirect('travelAi')

# this is the view for handling errors
def error_handler(request):
    return render(request, 'travelapp/page_not_found.html')
from django.shortcuts import redirect

def upload_Form(request):
    if request.method == 'POST':
        form = DestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'travelapp/mail.html',)
        else:
            context = {'form': form}
            return render(request, 'travelapp/fplaces.html', context)

    context = {'form': DestForm()}
    return render(request, 'travelapp/fplaces.html', context)


def ver_user(request):
    if request.method == 'POST':
        form = VerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            return redirect('getplaces')
        else:
            context = {'form': form}
            return render(request, 'travelapp/veruser.html', context)

    context = {'form': VerForm()}
    return render(request, 'travelapp/veruser.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email=request.POST['email']
        password = request.POST['password']
        # Retrieve other fields similarly

        # Create a new user object
        signup = SignUp(username=username, email=email, password=password)
        signup.save()

        # Save additional details to your custom model


        # Redirect to a success page or wherever needed
        return redirect('signup')

    return render(request, 'travelapp/login.html')
from django.contrib import messages

def logged(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check if user exists in your database
        user_exists = SignUp.objects.filter(email=email, password=password).exists()

        if user_exists:
            # User authenticated, redirect to success page
            return redirect('home')
        else:
            # User not found or invalid credentials, display error message
            messages.error(request, {'error_message': 'Invalid email or password'})
            return redirect('login')

    return render(request, 'travelapp/login.html')



import json
from django.http import HttpResponse
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='#',
    client_secret='#'
)

# hotels/views.py

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def hotel_list(request):
    city_name = request.GET.get('city_name','Pune')  # Default to Pune if no city name is provided
    hotels = get_hotels_by_city(city_name)

    if hotels is None:
        # Handle the case where hotels is None (e.g., display an error message or redirect)
        return HttpResponse("No hotels found for this city.")

    paginator = Paginator(hotels, 5)  # Show 5 hotels per page
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'travelapp/hotels.html', { 'city_name': city_name, 'page_obj': page_obj })

def get_hotels_by_city(city_name,limit=25):
    try:
        response = amadeus.reference_data.locations.get(keyword=city_name, subType="CITY").data[0]
        city_code = response['address']['cityCode']
        hotels_data = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code).data

        # Extract hotel details including latitude and longitude for the first 5 hotels
        hotel_ids = [hotel['hotelId'] for hotel in hotels_data[:limit]]

        hotels = []
        for hotel in hotels_data[:limit]:
            hotel_id = hotel['hotelId']
            hotel_details = {
                'name': hotel['name'],
                'address': hotel.get('address', {}).get('countryCode'),
                'latitude': hotel.get('geoCode', {}).get('latitude'),
                'longitude': hotel.get('geoCode', {}).get('longitude'),
                 # Include sentiments data
            }
            hotels.append(hotel_details)

        return hotels
    except (ResponseError, IndexError, KeyError) as error:
        print("Error occurred:", error)
        return None
