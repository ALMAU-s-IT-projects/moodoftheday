from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Emotion)
admin.site.register(ImageOption)
admin.site.register(Track)
admin.site.register(Quote)
admin.site.register(MoodEntry)