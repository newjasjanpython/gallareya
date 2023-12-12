from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import *

# Register your models here.


class MyModelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'display_about')

    def display_name(self, obj):
        return format_html('<h3>{}</h3>'.format(obj.get_name()))

    display_name.short_description = 'Name'

    def display_about(self, obj):
        return Truncator(obj.about).chars(55)

    display_about.short_description = 'About'

admin.site.register(Artist, MyModelAdmin)
admin.site.register(Art, MyModelAdmin)
admin.site.register(Feedback)
admin.site.register(WebUser)
admin.site.register(Category)
