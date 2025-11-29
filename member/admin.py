from django.contrib import admin
from .models import Member, Ministry, CommunityLeader, TestDb

# Register your models here.

admin.site.register(Member)
admin.site.register(Ministry)
admin.site.register(CommunityLeader)
