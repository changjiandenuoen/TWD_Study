from django import forms
from rango.models import Page, Category
from django.contrib.auth.models import User
from rango.models import UserProfile


class CategoryForm(forms.ModelForm):

    name = forms.CharField(max_length=Category.NAME_MAX_LENGTH, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    # the reason we set required to false is that:
    # the model will be responsible for populating the field when the form 
    # is eventually saved.
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # By using Meta inner class, we define which model we're wanting to provide a form for.
    class Meta:

        model = Category
        fields = ('name',)


class PageForm(forms.ModelForm):

    title = forms.CharField(max_length=Page.TITLE_MAX_LENGTH, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=Page.URL_MAX_LENGTH, help_text="Please enter the URL of the page.")

    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page

        # Hide the foreign key( category ), which means it will not include in the form
        # or we can use：
        # fields = ('title', 'url', 'views')
        exclude = ('category',)

    def clean(self):
        cleaned_data = self.cleaned_data

        # if a user does not enter a value into a form field
        # its entry will not exist in the cleaned_data dict
        # .get() would return None rather than raise a keyerror
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = f'http://{url}'
            cleaned_data['url'] = url

        return cleaned_data


class UserForm(forms.ModelForm):
    
    # By using PasswordInput method, html will hide when user input their password
    password = forms.CharField(widget=forms.PasswordInput())

    # describe additional information
    # model = User means UserForm class associate with User Model
    # Here we only want to show name, email, password for a user.
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
