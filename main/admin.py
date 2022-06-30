from django.contrib import admin
from .models import Inductee, Responsible_person, Message, Notification, Subpoena, Recruiting_office, Military_ID, City, Answer_Message
# Register your models here.

admin.site.register(Inductee)
admin.site.register(Responsible_person)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Answer_Message)
admin.site.register(Subpoena)
admin.site.register(Recruiting_office)
admin.site.register(Military_ID)
admin.site.register(City)