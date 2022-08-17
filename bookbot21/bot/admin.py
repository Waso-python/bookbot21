from django.contrib import admin

from .models import SchoolObject, Status, ObjectType, Booking, Role, Campus, User


admin.site.register(SchoolObject)
admin.site.register(Status)
admin.site.register(ObjectType)
admin.site.register(Booking)
admin.site.register(Role)
admin.site.register(Campus)
admin.site.register(User)
