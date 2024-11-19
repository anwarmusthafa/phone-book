from django.contrib import admin
from .models import Contact, SpamReport, CustomUser,GlobalDatabase

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Contact)
admin.site.register(SpamReport)
admin.site.register(GlobalDatabase)

