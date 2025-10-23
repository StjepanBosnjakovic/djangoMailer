"""
Custom authentication views with rate limiting for security.
"""
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class RateLimitedLoginView(auth_views.LoginView):
    """
    Custom login view with rate limiting to prevent brute force attacks.
    Limits to 5 login attempts per minute per IP address.
    """
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        # Check if rate limited
        if getattr(self.request, 'limited', False):
            form.add_error(None, "Too many login attempts. Please try again in a minute.")
        return super().form_invalid(form)


@ratelimit(key='ip', rate='3/h', method='POST')
def register_view(request):
    """
    User registration view with rate limiting.
    Limits to 3 registration attempts per hour per IP address.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Check if rate limited
        if getattr(request, 'limited', False):
            form = UserCreationForm(request.POST)
            form.add_error(None, "Too many registration attempts. Please try again later.")
            return render(request, 'registration/register.html', {'form': form})

        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
