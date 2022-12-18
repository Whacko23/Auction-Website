from django.contrib import admin
from .models import User, Categories, Auction, Bids, Comments
# Register your models here.

admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Categories)
admin.site.register(Bids)
admin.site.register(Comments)

