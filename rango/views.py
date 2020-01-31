from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category
from rango.models import Page


def index(request):
    # Query the database for a list of all category
    # Order the categories by the number of likes in descending order

    # -likes means in descending order
    # [:5] means top from first index to 5th index (top 5), return a subset of Category objects
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    return render(request, 'rango/about.html', context=None)


def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the tmplate rendering engine
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
