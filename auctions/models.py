from operator import truediv
from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    item_name = models.CharField(max_length=128)
    item_description = models.TextField()
    starting_price = models.DecimalField(decimal_places=2, max_digits=8, validators=[MinValueValidator(0.01)]) 
    image = models.ImageField(upload_to="", blank=True, default="noimage.svg.png")
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item_name} offered by {self.user}"


class Bid(models.Model):
    bid_amount = models.DecimalField(decimal_places=2, max_digits=8, validators=[MinValueValidator(0.01)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"${self.bid_amount} for {self.auction} by {self.user}"


class Comment(models.Model):
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment on {self.auction} by {self.user}"


class Watchlist(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlists")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"{self.auction} watched by {self.user}"
        