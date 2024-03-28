from django.contrib import admin
from .models import Destinations, Verify, SignUp
# Register your models here.
class DestinationAdmin(admin.ModelAdmin):
    list_display=['id','near_city','place','image','info']

admin.site.register(Destinations,DestinationAdmin)

class VerifyAdmin(admin.ModelAdmin):
    list_display=['id','username','email']

admin.site.register(Verify, VerifyAdmin)

class SignupAdmin(admin.ModelAdmin):
    list_display=['id','username','email','password']

admin.site.register(SignUp,SignupAdmin)
