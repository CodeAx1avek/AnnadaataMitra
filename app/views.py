from django.shortcuts import render
from django.http import JsonResponse
from groq import Groq
import json
import re
from django.shortcuts import render, redirect
from .forms import FarmerRegistrationForm
from django.contrib import messages
from .models import Product
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Initialize the Groq API client with your key
client = Groq(api_key="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")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Product
from .forms import UserRegistrationForm, FarmerRegistrationForm, ProductForm

def home(request):
    """Home view showing available products that are not expired."""
    products = Product.objects.filter(expiry_date__gte=now().date())
    return render(request, 'home.html', {'products': products})

def register(request):
    """Registration view for new users and farmers."""
    if request.method == 'POST':
        print("Request POST Data:", request.POST)  # Log the POST data
        user_form = UserRegistrationForm(request.POST)
        farmer_form = FarmerRegistrationForm(request.POST, request.FILES)

        if user_form.is_valid() and farmer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # Hash the password
            user.save()
            farmer = farmer_form.save(commit=False)
            farmer.user = user
            farmer.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            # Log form errors
            print("User Form Errors:", user_form.errors)
            print("Farmer Form Errors:", farmer_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegistrationForm()
        farmer_form = FarmerRegistrationForm()

    return render(request, 'users/register.html', {'user_form': user_form, 'farmer_form': farmer_form})

def login_view(request):
    """Login view for users."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Log the user in
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            messages.error(request, 'Invalid username or password.')  # Show error message
    
    return render(request, 'users/login.html')

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product, Farmer  # Ensure Farmer is imported

def farmer_dashboard(request):
    # Fetch the Farmer instance based on the logged-in user
    farmer = get_object_or_404(Farmer, user=request.user)
    products = Product.objects.filter(farmer=farmer)

    form = ProductForm()

    if request.method == 'POST':
        if 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.farmer = farmer  # Associate the product with the Farmer instance
                product.save()
                return redirect('dashboard')

        elif 'update_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect('dashboard')

        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            return redirect('dashboard')

    return render(request, 'dashboard.html', {'form': form, 'products': products})
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class CustomLogoutView(LogoutView):
    # Redirect to thank you page after logout
    next_page = reverse_lazy('logout_thank_you')  # This should match the URL name of the thank you page

class LogoutThankYouView(TemplateView):
    template_name = 'logout_thank_you.html' 

# chatbot purpose ----------------------------------------------------------------

def detect_language(message):
    """Detect the language of the user message."""
    # Simple regex to check for Hindi characters
    if re.search(r'[\u0900-\u097F]', message):
        return 'hi'  # Hindi
    # Add checks for other Indian languages as needed
    return 'en'  # Default to English

def generate_response(user_message):
    """Interact with Groq API and generate a response focused on farming."""
    farming_context = (
        "You are an AI assistant designed to provide information and assistance specifically for farmers. "
        "Please respond with advice, tips, and information related to agriculture, crop management, "
        "livestock care, sustainability, and related topics."
    )

    # Check if the message is in Hindi
    is_hindi = any(u'\u0900' <= c <= u'\u097F' for c in user_message)  # Check for Hindi Unicode range
    if is_hindi:
        farming_context += " Respond in Hindi if the user types in Hindi."

    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {"role": "system", "content": farming_context},  # Provide context to the AI
            {"role": "user", "content": user_message}
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=False,  # Disable streaming for backend response handling
    )

    # Correctly access the content from the message
    return completion.choices[0].message.content if completion.choices else "No response generated."

def chatbot(request):
    return render(request, "chatbot.html")

# endhere chatbot -----------------------------------------------------------------------------------------

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only for debugging; should be removed in production!
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load JSON data
            user_message = data.get('message')  # Get the user's message
            
            if user_message:
                response = generate_response(user_message)  # Your function to generate a response
                return JsonResponse({'response': response})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings

# Load location data from JSON file
json_file_path = os.path.join(settings.BASE_DIR, 'app', 'locations.json')
with open(json_file_path) as f:
    data = json.load(f)
from django.http import JsonResponse

@csrf_exempt
def get_suggestions(request):
    if request.method == "GET":
        query = request.GET.get('query', '').strip()
        state = request.GET.get('state', '').strip()
        district = request.GET.get('district', '').strip()

        states = []
        districts = []
        cities = []

        # Iterate over location details
        for location in data["location_details"]:
            # Get states
            if not state and location["State"].lower().startswith(query.lower()):
                if location["State"] not in states:
                    states.append(location["State"])
            # Get districts
            if state and location["State"].lower() == state.lower():
                if location["District"] not in districts:
                    districts.append(location["District"])
            # Get cities
            if district and location["District"].lower() == district.lower():
                if location["City"] not in cities:
                    cities.append(location["City"])

        response_data = {
            "states": states,
            "districts": districts,
            "cities": cities,
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

