from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import User, Listing, Bid, Category, Comment, Watchlist


# INDEX PAGE
def index(request):
    active_listings = Listing.objects.all().filter(active=True)
    return render(
        request,
        "auctions/index.html",
        {"auctions": active_listings, "title": "Active Auctions"},
    )


# LOGIN; LOGOUT; REGISTER
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# CATEGORY LIST AND VIEW
# Renders the category overview and passes list of categories to the html
def category_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


# Renders page with all active auctions for specific category
def category_list(request, category):
    try:
        category_name = Category.objects.get(category=category)
        auctions = Listing.objects.all().filter(category=category_name)
    except:
        return render(request, "auctions/no_auction.html")
    return render(
        request, "auctions/category.html", {"auctions": auctions, "category": category}
    )


# Tries to render the specific auction by pk/id, on exception renders an error page
def auction_view(request, pk):
    try:
        auction = Listing.objects.get(pk=pk)
    except:
        return render(request, "auctions/no_auction.html")

    return render(request, "auctions/auction.html", {"auction": auction, "pk": pk})


# Defines Form for new auction listing
class AuctionForm(ModelForm):
    class Meta:
        model = Listing
        fields = [
            "item_name",
            "item_description",
            "starting_price",
            "image",
            "image_url",
            "category",
        ]


# Renders the new listing page with form. When form is submitted, the auction page gets opened
def new_listing(request):
    form = AuctionForm(request.POST)
    if form.is_valid():
        new_listing = form.save(
            commit=False
        )  # Saving the form without passing it to the db, because...
        new_listing.user = request.user  # Current User needs to be added
        new_listing.save()

        url = reverse("auction", kwargs={"pk": new_listing.pk})
        return HttpResponse(url)

    else:
        return render(request, "auctions/new_listing.html", {"form": form})
