from django.contrib import admin

from .models import Run,RunLocation,Territory,User

admin.site.register(Run)
admin.site.register(RunLocation)
admin.site.register(Territory)
admin.site.register(User)

