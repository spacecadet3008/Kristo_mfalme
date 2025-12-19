from django.shortcuts import render, redirect

from django.http import JsonResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

from .forms import UserForm, SignupForm
from .models import UserProfile

from member.models import CommunityLeader


def login_user(request):
    template = "registration/login.html"
    form = UserForm()
    context = {"form": form}
    return render(request, template, context)


def _logout(request):
    user = request.user
    logout(request)
    return redirect("login_user")


def _login(request):
    if request.method == "POST":
        # import pdb; pdb.set_trace()
        form = UserForm(request.POST or None)
        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            next_url = request.POST.get("next") or "home"

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # import pdb; pdb.set_trace()
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid Username or Password")
                return redirect(next_url)


def signup(request):
    template = "registration/signup.html"
    form = SignupForm()
    context = {"form": form}
    return render(request, template, context)


def signup_user(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        
        if form.is_valid():
            # Check for existing users
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "User with that username already exists")
                return render(request, "registration/signup.html", {"form": form})
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "User with that email already exists")
                return render(request, "registration/signup.html", {"form": form})
            
            # Save the user
            user = form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect("home")  # Redirect to login after successful registration
            
        else:
            # Form has errors - re-render with error messages
            return render(request, "registration/signup.html", {"form": form})
    
    else:
        # GET request - show empty form
        form = SignupForm()
        return render(request, "registration/signup.html", {"form": form})


def user_profile(request):
    # SLTGhana = 030 223 1886
    template = "registration/user_profile.html"
    profile = UserProfile.objects.get_or_create(user=request.user)
    try:
        shepherd = CommunityLeader.objects.get(name=request.user.username)
        members = CommunityLeader.member_set.active()
        # import pdb; pdb.set_trace()
    except:
        shepherd = None
        members = None
    # import pdb; pdb.set_trace()
    context = {"profile": profile, "members": members, "shepherd": shepherd}
    return render(request, template, context)


def login_api(request):
    if request.method == "POST":
        form = UserForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    response = {"STATUS": "OK", "USER_ID": user.pk}
                    return JsonResponse(response, content_type="Application/json", safe=False)
                else:
                    response = {"STATUS": "INACTIVE"}
                    return JsonResponse(response, content_type="Application/json", safe=False)
            else:
                response = {"STATUS": "INVALID USER CREDENTIALS", "CODE": -1}
                return JsonResponse(response, content_type="Application/json", safe=False)

        else:
            response = {"STATUS": "VALIDATION ERROR"}
            return JsonResponse(response, content_type="Application/json", safe=False)


def signup_api(request):
    if request.method == "POST":
        form = SignupForm(request.POST or None)
        if form.is_valid():
            form.save()
            response = {"STATUS": "OK", "CODE": 0}
            return JsonResponse(response, content_type="Application/json", safe=False)
        else:
            response = {"STATUS": "ERROR", "CODE": -1}
            return JsonResponse(response, content_type="Application/json", safe=False)
