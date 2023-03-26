from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login as dj_login, authenticate, logout
from users.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, ServerRegistrationForm
from django.contrib import messages
from django.template import loader
from users.models import Account, Server
from django.urls import reverse
from blog.models import BlogPost
# Create your views here.

def index(request):
    all_users = Account.objects.all()
    template = loader.get_template('users/home.html')
    return HttpResponse(template.render({"users":all_users}, request))

def registration_view(request):
    context = {}
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                email = form.cleaned_data.get('email')
                raw_password = form.cleaned_data.get('password1')
                account = authenticate(email=email, password=raw_password)
                dj_login(request, account)
                return HttpResponseRedirect(reverse('users:index'))
            else:
                context['registration_form'] = form
        else:
            form = RegistrationForm()
            context['registration_form'] = form
        return render(request=request, template_name="users/register.html", context={"registration_form":form})
    else:
        return redirect('users:index')

def login_view(request):
    user = request.user
    if user.is_authenticated:
        return redirect('users:index')
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            email.lower()
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                dj_login(request, user)
                return redirect('users:index')
    
    else:
        form = AccountAuthenticationForm()
    return render(request, 'users/login.html', context={'form':form})

def logout_view(request):
    logout(request)
    return redirect('users:index')

def account_view(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context['success_message'] = "Account Updated"
        
    else:
        form = AccountUpdateForm(initial={"email": request.user.email, "username":request.user.username})
    
    blog_posts = BlogPost.objects.filter(author=request.user)
    server_list = Server.objects.filter(account=request.user)
    context["account_form"] = form
    context["blog_posts"] = blog_posts
    context['server_list'] = server_list
    return render(request, "users/account.html", context)

def must_authenticate_view(request):
    return render(request, "users/must_authenticate.html", context={})

def server_registration_view(request):
    if not request.user.is_authenticated:
        return redirect('users:must_authenicate')

    form = ServerRegistrationForm(request.POST or None)
    context = {}
    if form.is_valid():
        obj = form.save(commit=False)
        account = Account.objects.filter(email=request.user.email).first()
        obj.account = account
        obj.save()
        form = ServerRegistrationForm()
        context["success_message"]= "Server Added"
    
    context['form'] = form
    
    return render(request, 'users/add_server.html', context)

def server_update_view(request, listz_id):
    if not request.user.is_authenticated:
        return redirect('users:must_authenticate')
    server_id = Server.objects.get(pk=listz_id)
    if request.user == server_id.account:
        context = {}
        serverz = get_object_or_404(Server, pk=listz_id)
        context['serverz'] = serverz
        return render(request, 'users/server_update_view.html', context)
    return redirect('users:must_authenticate')


def server_update(request, listz_id):
    if not request.user.is_authenticated:
        return redirect('users:must_authenticate')
    server_id = Server.objects.get(pk=listz_id)
    if request.user == server_id.account:
        context = {}
        if request.method == 'POST':
            serverz = get_object_or_404(Server, pk=listz_id)
            serverz.ip = request.POST['ip']
            serverz.port = request.POST['port']
            serverz.save()
            context['serverz'] = serverz
            context['success_message'] = "Server Updated"
            return render(request, 'users/server_update_view.html', context)
    
    else:
        context['success_message'] = "Update Failure"
        return render(request, 'users/server_update.html', context)
    
def server_delete(request, listz_id):
    if not request.user.is_authenticated:
        return redirect('users:must_authenticate')
    server_id = Server.objects.get(pk=listz_id)
    if request.user == server_id.account:
        context = {}
        serverz = get_object_or_404(Server, pk=listz_id)
        serverz.delete()
        return redirect('users:account')
    return redirect('users:must_authenticate')
