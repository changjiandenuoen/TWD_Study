from django.contrib import admin
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    # The elements in this tuple are attributes in page model
    list_display = ('title', 'category', 'url')


admin.site.register(Category)
admin.site.register(Page, PageAdmin)