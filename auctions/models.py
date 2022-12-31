from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import When

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    pass

    def __str__(self) -> str:
        return self.username

class Categories(models.Model):
    category = models.CharField(max_length=60, primary_key=True)
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.category


class Auction(models.Model):
    id = models.BigAutoField(primary_key=True)
    name_of_product = models.CharField(max_length=200)
    buyout_price = models.IntegerField()
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    category = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name='auctions')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    closed = models.BooleanField(default=False)
    winner = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    allotted_time = models.IntegerField()
    image = models.ImageField(upload_to="images/product/%Y/%m", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name_of_product} by {self.listed_by}"


class Bids(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.IntegerField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE,related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self) -> str:
        return f"$ {self.amount} by {self.posted_by}"

class Comments(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True ,related_name='comments')
    comment = models.TextField()
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments')
    posted_at = models.DateTimeField(auto_now_add=True, editable=False)
    subcomment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcomments')

    def __str__(self) -> str:
        return f"{self.comment[:50]}..." if len(self.comment) > 50 else f"{self.comment}"