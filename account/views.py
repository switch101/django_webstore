from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import CustomUserCreationForm, UserUpdateForm

from django.contrib import messages


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please sign in.')
            return redirect('signin')
        else:
            messages.error(request, 'Error creating account. Please correct the errors below.')
            return render(request, 'accounts/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='StoreAdmin').exists():
                return redirect(reverse('store:dashboard'))
            else:
                return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/signin.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required(login_url='account/signin')
def account_settings(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('account_settings')
        else:
            # Print form errors to console for debugging
            print(form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/settings.html', {'form': form})