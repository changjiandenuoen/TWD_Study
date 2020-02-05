
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category
from rango.models import Page

from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

from datetime import datetime


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine
    context_dict = {}

    try:
        # get the category name slug, if cannot get, raise a DoesNotExist exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages
        # The filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # add page list into context dictionary 'pages'
        context_dict['pages'] = pages

        # add cateogry list into context dictionary 'category'
        context_dict['category'] = category

    except Category.DoesNotExist:

        # We get here if we didn't find the specified category
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render everything together
    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):

    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():

            # save the new category to the database
            form.save(commit=True)
            # after saving the category, redirect back to index view
            return redirect(reverse('rango:index'))

        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))

        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    # A boolean value for telling the template whether the registration was successful
    # Set to False initially, use code change the value to True when registration succeeds
    registered = False

    # If it is a HTTP POST, we r interested in processing from data
    if request.method == 'POST':

        # grab information form the raw form information
        # Note that we use both UserForm and UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method
            # Once hashed, we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance
            # Since we need to set the user attribute oursleves
            # we set commit=False which delays saving the model
            profile = profile_form.save(commit=False)
            profile.user = user

            # check whether the user provided a profile picture
            # If so, get it from the input form and put it in UserProfile Model
            if 'picture' in request.FILES:
                profile.picture = request.FILES('picture')

            # Now we can save
            profile.save()

            # Update our variable to indicate that the template registration was successful
            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        # Not a HTTP POST, so we render our form using ModelForm instances
        # These forms will be blank, ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()


    # Render the template depending on the context
    return render(request, 
                  'rango/register.html',
                  context={'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})


def user_login(request):
    if request.method == 'POST':

        # This information is obtained from the login form
        # We use request.POST.get('<varible>')  rather than request.POST['<varible>']
        # because the request.POST.get return None if value does not exist
        # but request.POST['<varible>'] will return exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use authenticate method to check if the username/password combination is valid
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                # log in successful
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # user is not active, cannot log in!
                return HttpResponse("Your Rango account is disabled")

        else:
            # wrong input, cannot log in!
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")

    else:
        # If it is a GET request
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):

    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')


    # If more than a day since the last visit
    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1

        # Update the last visit cookie now that we have update the count
        request.session['last_visit'] = str(datetime.now())

    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits