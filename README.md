# Django Admin Customization

...

## Introduction

django admin is one of the biggest strength of django 
allows you to easily manipulate data, provides forms, user-friendly UI
it’s extremely customizable but a lot of folks don’t know how to adapt it to their project
this article looks at just that

## Objectives

By the end of this tutorial, you'll be able to:

1. Perform basic Django admin site configuration
1. Explain how Django model attributes affect the admin site
1. Use `list_display` to control which model fields are displayed
1. Add custom model fields to `list_display` and format existing ones
1. Add links to related model objects via foreign keys
1. Enable sorting, ordering, and filtering functionality
1. Handle model inlines for both `N:1` and `M:M` relationships
1. Use Django admin actions and create custom ones
1. Override Django admin templates & forms
1. Utilize `djangoql` for advanced searching functionality
1. Utilize `django-import-export` to easily import and export model data
1. Modify the appearance of your admin site via `django-admin-interface`

---
---
---

## Project Setup

To demonstrate the different customization concepts I've prepared an event ticket sales webapp that we'll use throughout the tutorial. The webapp allows us to manage venues, concerts, concert categories, and tickets.

Its database has the following entity-relationship model:

![Tickets ER Model](https://i.ibb.co/3cLbMTD/tickets-er-model.png)

> I suggest you to follow along with this exact project since it's setup in such a way that'll make it easy to demonstrate all the concepts. After the tutorial, you can work on your own projects.


First, grab the source code from the [repository](https://github.com/duplxey/django-admin-customization/tree/base) on GitHub:

```sh
$ git clone git@github.com:duplxey/django-admin-customization.git --branch base 
$ cd django-admin-customization
```

Create a virtual environment and activate it:

```sh
$ python3.11 -m venv env && source env/bin/activate
```

Install the requirements and migrate the database:

```sh
(venv)$ pip install -r requirements.txt
(venv)$ python manage.py migrate
```

Create a superuser and populate the database:

```sh
(venv)$ python manage.py createsuperuser
(venv)$ python manage.py populate_db
```

Run the development server:

```sh
(venv)$ python manage.py runserver
```

Open your favorite web browser and navigate to [http://localhost:8000/admin](http://localhost:8000/admin). Try using your superuser credentials to access the Django admin site

If everything goes well you should get the `Successfully populated the database` message. Start the development server (if it isn't running already) and navigate to your admin dashboard once again. Then check if the database was populated with some venues, concert categories, concerts, and tickets.

## Basic Admin Site Customization

Before diving into advanced Django admin site customization, let's look at the default

- changing the admin URL

```python
# core/urls.py

urlpatterns = [
    path("secretadmin/", admin.site.urls),
]
```

- changing basic Django admin variables


```python
# core/urls.py

admin.site.site_title = "TicketsPlus site admin"
admin.site.site_header = "TicketsPlus administration"
admin.site.index_title = "Site administration"
admin.site.site_url = "/"
admin.site.enable_nav_sidebar = True
admin.site.empty_value_display = "-"
```

> For other site settings check out Django's [sites.py source code](https://github.com/django/django/blob/main/django/contrib/admin/sites.py).

^ explain these basic options

## Django Model and Admin

explain the connection between Django models and Django Admin, e.g. `__str__`, and `Meta`

- `__str__` sets the display name (just mention), verbose_name, verbose_name_plural, ordering

```python
class ConcertCategory(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = "concert category"
        verbose_name_plural = "concert categories"
        ordering = ["-name"]

    def __str__(self):
        return f"{self.name}"  
```

should be lowercase, verbose_name and verbose_name_plural

problems usually arise when a noun ends with -y and then u make it plural, you can't just add 's', it needs to be ies or something like that

## Customize Admin Site with ModelAdmin Class

### Control List Display

- set `list_display` on `AdminModel` to make each field sortable and nicer displaya

```python
# tickets/admin.py

class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "price", "tickets_left"]
    readonly_fields = ["tickets_left"]
```

talk about venue n+1 and optimization, tell how much of a different it makes

```python
# tickets/admin.py

class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "price", "tickets_left"]
    list_select_related = ["venue"]
    readonly_fields = ["tickets_left"]
```

![N+1 problem](https://i.ibb.co/j66hbQR/concerts-unoptimized.png)

![N+1 optimized](https://i.ibb.co/m91ttGx/django-optimized-query.png)

then let's do the same for the `Ticket` model


```python
# tickets/admin.py

class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "capacity"]
    

class TicketAdmin(admin.ModelAdmin):
    list_display = ["customer_full_name", "concert", "payment_method", "paid_at", "is_active"]
    list_select_related = ["concert", "concert__venue"]
```


- adding custom fields to list_display (e.g. max, min, average), image thumbnails

let's add is sold out field

```python
# tickets/models.py

class Concert(models.Model):
    # ...
    
    def is_sold_out(self):
        return self.tickets_left == 0
```

```python
# tickets/admin.py

class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "tickets_left", "display_sold_out"]
    list_select_related = ["venue"]

    def display_sold_out(self, obj):
        return obj.is_sold_out()

    display_sold_out.short_description = "Sold out"
    display_sold_out.boolean = True
```

- let's format the existing price field to `$<price>`

```python
class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "display_price", "tickets_left", "display_sold_out"]
    # ...
    
    def display_price(self, obj):
        return f"${obj.price}"

    display_price.short_description = "Price"
    display_price.admin_order_field = "price"
```

### Link Related Model Objects

- linking to related objects and foreign keys + explain Django admin URL structure

| Page       | URL                              | Description                                     |
|------------|----------------------------------|-------------------------------------------------|
| List       | `%(app)s\_%(model)s\_changelist` | Displays the list of objects                    |
| Add        | `%(app)s\_%(model)s\_add`        | Object add form                                 |
| Change     | `%(app)s\_%(model)s\_change`     | Object change form (requires `objectId`)        |
| Delete     | `%(app)s\_%(model)s\_delete`     | Object delete form (requires `objectId`)        |
| History    | `%(app)s\_%(model)s\_history`    | Displays object's history (requires `objectId`) |

concerts, we want the venue to be clickable as well like so:

to do that, we have to do the following

```python
# tickets/admin.py

from django.urls import reverse
from django.utils.html import format_html

class ConcertAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["name", "display_venue", "starts_at", "display_price", "tickets_left", "display_sold_out"]
    list_select_related = ["venue"]

    # ...

    def display_venue(self, obj):
        link = reverse("admin:tickets_venue_change", args=[obj.venue.id])
        return format_html('<a href="{}">{}</a>', link, obj.venue)

    display_venue.short_description = "Venue"
```

Don't forget about the imports:

```python
from django.urls import reverse
from django.utils.html import format_html
```


### Sort, Filter & Search

sorting is automatically handled by Django admin, you can click on a property and it'll sort the table

filtering can be easily implemented like so:

```python
# tickets/admin.py

class ConcertAdmin(admin.ModelAdmin):
    # ...
    list_filter = ["venue"]
    # ...
```

you shouldn't use filter for fields with too many options, eg. `tickets_left` would result in a clusterfuck, because each number would be its own filter

to enable searching set the following property:

```
    search_fields = ["name", "venue__name", "venue__address"] 
```

you can of course refer to related fields via `__`

to add a custom filter e.g. soldout you can do it like this:

```python
# tickets/admin.py

from django.contrib.admin import SimpleListFilter

class SoldOutFilter(SimpleListFilter):
    title = "Sold out"
    parameter_name = "sold_out"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(tickets_left=0)
        else:
            return queryset.exclude(tickets_left=0)
```

then include it in `list_filter`:

```python
    list_filter = ["venue", SoldOutFilter]
```

![Django Admin Filters](https://i.ibb.co/QYtXdWS/django-admin-filters.png)

### Handle Model Inlines

- StackedInline, TabularInline

add read-only tabularinline to Venue to see concerts related to some venue (we can do this because of the ForeignKey)

```python
# tickets/admin.py

class ConcertInline(admin.TabularInline):
    model = Concert
    fields = ["name", "starts_at", "price", "tickets_left"]
    readonly_fields = ["name", "starts_at", "price", "tickets_left"]
    can_delete = False
    max_num = 0
    extra = 0
    show_change_link = True
    
    
class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "capacity"]
    inlines = [ConcertInline]
```

![Django Admin Tabular Inline](https://i.ibb.co/dBhDJpx/django-admin-inline.png)


ManyToMany is a little bit different

- [ModelAdmin](https://github.com/django/django/blob/d25f3892114466d689fd6936f79f3bd9a9acc30e/django/contrib/admin/options.py#L637) deep dive, most useful properties, list_display, read_only, etc.


### Custom Admin Actions

django also allows you to define custom actions, to demonstrate how it's done we'll add a bulk 
`is_active` toggle for our tickets

- [bulk actions](https://www.geeksforgeeks.org/customize-django-admin-interface/), eg. tag everything as active, inactive


```python
# tickets/admin.py

@admin.action(description="Activate selected tickets")
def activate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Deactivate selected tickets")
def deactivate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=False)


class TicketAdmin(admin.ModelAdmin):
    list_display = ["customer_full_name", "concert", "payment_method", "paid_at", "is_active"]
    list_select_related = ["concert", "concert__venue"]
    actions = [activate_tickets, deactivate_tickets]
```

![Django Admin Custom Action](https://i.ibb.co/YQ5Dvz7/django-admin-custom-action.png)

---
---
---

## Override Django Admin Forms

- override django admin forms (data validation)


```python
# tickets/forms.py

from django import forms
from django.forms import ModelForm, RadioSelect

from tickets.models import Ticket


class TicketAdminForm(ModelForm):
    first_name = forms.CharField(label="First name", max_length=32)
    last_name = forms.CharField(label="Last name", max_length=32)

    class Meta:
        model = Ticket
        fields = [
            "concert",
            "first_name",
            "last_name",
            "payment_method",
            "is_active"
        ]
        widgets = {
            "payment_method": RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = {}

        if instance:
            customer_full_name_split = instance.customer_full_name.split(" ", maxsplit=1)
            initial = {
                "first_name": customer_full_name_split[0],
                "last_name": customer_full_name_split[1],
            }

        super().__init__(*args, **kwargs, initial=initial)

    def save(self, commit=True):
        self.instance.customer_full_name = self.cleaned_data["first_name"] + " " + self.cleaned_data["last_name"]
        return super().save(commit)

```

```python
# tickets/admin.py

class TicketAdmin(admin.ModelAdmin):
    # ...
    form = TicketAdminForm

```

also import it:

```
from tickets.forms import TicketAdminForm
```

![Django Admin Override Form](https://i.ibb.co/S3cBWVc/django-admin-override-form.png)

## Override Django Admin Templates

Django admin site allows you to easily customize any visual aspect of it by overriding templates. All you have to do is:

1. Check out [Django's source code](https://github.com/django/django/tree/main/django/contrib/admin/templates) and copy the original template.
2. Paste the template in *templates/admin* or *templates/registration* respectively.
3. Modify the template to your likings.

As an example let's do it with the login page. First grab the original template:


```
<!-- django/contrib/admin/templates/admin/login.html -->

{% extends "admin/base_site.html" %}
{% load i18n static %}

{% block extrastyle %}{{ block.super }}<link rel="stylesheet" href="{% static "admin/css/login.css" %}">
{{ form.media }}
{% endblock %}

{% block bodyclass %}{{ block.super }} login{% endblock %}

{% block usertools %}{% endblock %}

{% block nav-global %}{% endblock %}

{% block nav-sidebar %}{% endblock %}

{% block content_title %}{% endblock %}

{% block nav-breadcrumbs %}{% endblock %}

{% block content %}
{% if form.errors and not form.non_field_errors %}
<p class="errornote">
{% blocktranslate count counter=form.errors.items|length %}Please correct the error below.{% plural %}Please correct the errors below.{% endblocktranslate %}
</p>
{% endif %}

{% if form.non_field_errors %}
{% for error in form.non_field_errors %}
<p class="errornote">
    {{ error }}
</p>
{% endfor %}
{% endif %}

<div id="content-main">

{% if user.is_authenticated %}
<p class="errornote">
{% blocktranslate trimmed %}
    You are authenticated as {{ username }}, but are not authorized to
    access this page. Would you like to login to a different account?
{% endblocktranslate %}
</p>
{% endif %}

<form action="{{ app_path }}" method="post" id="login-form">{% csrf_token %}
  <div class="form-row">
    {{ form.username.errors }}
    {{ form.username.label_tag }} {{ form.username }}
  </div>
  <div class="form-row">
    {{ form.password.errors }}
    {{ form.password.label_tag }} {{ form.password }}
    <input type="hidden" name="next" value="{{ next }}">
  </div>
  {% url 'admin_password_reset' as password_reset_url %}
  {% if password_reset_url %}
  <div class="password-reset-link">
    <a href="{{ password_reset_url }}">{% translate 'Forgotten your password or username?' %}</a>
  </div>
  {% endif %}
  <div class="submit-row">
    <input type="submit" value="{% translate 'Log in' %}">
  </div>
</form>

</div>
{% endblock %}
```

There's a bunch of blocks we won't be using so let's just keep the {content_title one}.

```html
<!-- templates/admin/login.html -->

{% extends "admin/login.html" %}

{% block content_title %}
    <p style="background: #ffffcc; padding: 10px 8px">
        This is a really important message.
    </p>
{% endblock %}
```

![Django Admin Override Template](https://i.ibb.co/YNRZTfG/django-admin-override-template.png)

That's it!

---
---
---

## Advanced Search with DjangoQL

[DjangoQL](https://github.com/ivelum/djangoql) is a powerful 3rd-party package that allows you to perform advanced queries without relying on raw SQL. It has its own syntax and auto-completion, supports logical operators, and works for any Django model.

Start by installing the package:

```sh
(env)$ pip install djangoql==0.17.1
```

Add to `INSTALLED_APPS` in *core/settings.py*:

```python
# core/settings.py

INSTALLED_APPS = [
    # ...
    "djangoql",
]
```

Next, add `DjangoQLSearchMixin` as the parent class to all `ModelAdmin`s where you want to enable advanced searching capabilities.

Let's add it to the `TicketAdmin` for example:

```python
# tickets/models.py

class TicketAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    # ...
```

Don't forget about the import:

```python
from djangoql.admin import DjangoQLSearchMixin
```

You can now use the same search box as before to perform advanced queries. Examples:

1. `is_active = True` returns active tickets
2. `payment_method = "ET" or payment_method = "BC"` returns tickets purchased with crypto
4. `concert.venue.name ~ "Amphitheatre"` returns tickets for concerts in amphitheatres
5. `concert.tickets_left > 500` returns tickets for concerts with more than 500 tickets left

> For more information on DjangoQL language check out [DjangoQL language reference](https://github.com/ivelum/djangoql#language-reference).

## Import and Export Data with Django Import Export

In this section, we'll look at how to import and export object data via [`django-import-export`](https://django-import-export.readthedocs.io/en/latest/). Django import/export is an excellent package for easily importing and exporting data in different formats, including JSON, CSV, and YAML. The package also comes with built-in admin integration.

First, install it:

```sh
(env)$ pip install django-import-export==3.2.0
```

Next, add it to `INSTALLED_APPS` in *core/settings.py*:

```python
# core/settings.py

INSTALLED_APPS = [
    # ...
    "import_export",
]
```

Collect the static files:

```sh
(env)$ python manage.py collectstatic
```

After that, add `ImportExportActionModelAdmin` as the parent class to all the `ModelAdmin`s you want to be importable/exportable. 

Here's an example for the `TicketAdmin`:

```python
# tickets/admin.py

class TicketAdmin(DjangoQLSearchMixin, ImportExportActionModelAdmin):
    # ...
```

Don't forget about the import:

```python
from import_export.admin import ImportExportActionModelAdmin
```

> If you want a model to be exportable-only use `ExportActionModelAdmin`.

If you navigate to your ticket page now, you should see that the export action has been added. Test it by selecting a few tickets, the wanted format, and clicking "Go". Django should download the export as a file to your local PC.

You can test the import functionality by importing the just exported file.

![Django Import / Export Admin](https://i.ibb.co/V3JDqKH/django-import-export-example.png)

## Style Admin Site with Django Admin Interface

Customizing the appearance of the admin site through template overriding can be awkward. You might accidentally break stuff, Django admin templates may change in the future, and it'll be a hassle to maintain.

A better approach to styling your admin site is using the [`django-admin-interface`](https://github.com/fabiocaccamo/django-admin-interface) package. This package comes with beautiful premade admin interface themes and allows you to customize different aspects of your admin site easily. That includes changing the colors, strings, favicon, logo, and more.

Start by installing it via pip:

```
(env)$ pip install django-admin-interface==0.26.0
```

Next, add `admin_interface` and `colorfield` to `INSTALLED_APPS` before `django.contrib.admin`:

```python
# core/settings.py

INSTALLED_APPS = [
    #...
    "admin_interface",
    "colorfield",
    #...
    "django.contrib.admin",
    #...
]

X_FRAME_OPTIONS = "SAMEORIGIN"              # allows you to use modals insated of popups
SILENCED_SYSTEM_CHECKS = ["security.W019"]  # ignores redundant warning messages
```

Migrate the database:

```
(env)$ python manage.py migrate
```

Collect static files:

```
(env)$ python manage.py collectstatic --clear
```

Start the development server and navigate to [http://localhost:8000/secretadmin](http://localhost:8000/secretadmin). You'll notice that your Django admin site looks more modern, and there'll be an "Admin Interface" section.

![Django Admin Interface Default Theme](https://i.ibb.co/9qX80wg/django-admin-interface-default.png)

Click "Admin Interface > Themes" to see all the currently installed themes. By default, there should be only one theme called "Django". If you wish, you can install three more themes via fixtures:

```
(env)$ python manage.py loaddata admin_interface_theme_bootstrap.json
(env)$ python manage.py loaddata admin_interface_theme_foundation.json
(env)$ python manage.py loaddata admin_interface_theme_uswds.json
```

Clicking on an existing theme allows you to customize all the previously mentioned aspects.

![Django Admin Interface Theme Customization](https://i.ibb.co/jLQmCBf/django-admin-interface-customization.png)

## Conclusion

- https://testdriven.io/blog/django-charts/
- https://testdriven.io/blog/multiple-languages-in-django/
- https://testdriven.io/blog/django-custom-user-model/

Grab the final source code from [django-admin-customization](https://github.com/duplxey/django-admin-customization) GitHub repo.
