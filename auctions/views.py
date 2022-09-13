from typing import List
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import User, Listing, Bid, Category, Comment, Watchlist


def index(request):
    """
    View: Passing all active auctions to index.html
    """
    active_listings = Listing.objects.all().filter(active=True)
    return render(
        request,
        "auctions/index.html",
        {"auctions": active_listings, "title": "Active Auctions"},
    )


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


def category_view(request):
    """
    View: Passes all categories to categories.html
    """
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


def category_list(request, category):
    """
    View: Passes all auctions per category to the category specific html
    """
    try:
        category_name = Category.objects.get(category=category)
        auctions = Listing.objects.all().filter(category=category_name)
    except:
        return render(request, "auctions/no_auction.html")
    return render(
        request, "auctions/category.html", {"auctions": auctions, "category": category}
    )


def auction_view(request, pk):
    """
    View: Passes all auction details to the auction specific html
    """
    try:
        auction = Listing.objects.get(pk=pk)
    except:
        return render(request, "auctions/no_auction.html")

    if Bid.objects.filter(auction=auction).exists() == False:
        highest_bid = 0
    else:
        highest_bid = Bid.objects.filter(auction=auction).latest("bid_amount")

    watch_exists = (
        Watchlist.objects.all()
        .filter(auction=auction)
        .filter(user=request.user)
        .exists()
    )

    return render(
        request,
        "auctions/auction.html",
        {
            "auction": auction,
            "pk": pk,
            "bidform": BidForm(),
            "highest_bid": highest_bid,
            "exists": watch_exists,
        },
    )


class AuctionForm(ModelForm):
    """
    Form: Create new auction listing
    """

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


def new_listing(request):
    """
    View: Passes the form to the new_listing.html. If form is submitted, create new auction and render auction page
    """
    form = AuctionForm(request.POST)
    if form.is_valid():
        new_listing = form.save(
            commit=False
        )  # Saving the form without passing it to the db, because...
        new_listing.user = request.user  # Current User needs to be added
        new_listing.save()

        url = reverse("auction", kwargs={"pk": new_listing.pk})
        return HttpResponseRedirect(url)

    else:
        return render(request, "auctions/new_listing.html", {"form": form})


class BidForm(ModelForm):
    """
    Form: Make a bid
    """

    class Meta:
        model = Bid
        fields = ["bid_amount"]


def make_bid(request, pk):
    """
    View: When BidForm gets submitted, check for valid bid and place it. Otherwise redirect to error page.
    """
    bidform = BidForm(request.POST)

    if bidform.is_valid():
        auction = Listing.objects.get(pk=pk)
        user = request.user
        bid = bidform.save(commit=False)
        starting_bid = auction.starting_price
        current_bids = Bid.objects.all().filter(auction=auction)

        check_start = bid.bid_amount >= starting_bid

        def check_current():
            for current_bid in current_bids:
                if bid.bid_amount < current_bid.bid_amount:
                    return False
            return True

        if check_start and check_current():
            bid.auction = auction
            bid.user = user
            bid.save()
        else:
            return render(request, "auctions/no_auction.html")

    url = reverse("auction", kwargs={"pk": pk})
    return HttpResponseRedirect(url)


def watchlist(request):
    """
    View: Renders the watchlist for logged in user.
    """
    user = request.user
    auctions = Watchlist.objects.all().filter(user=user)
    return render(
        request, "auctions/watchlist.html", {"user": user, "auctions": auctions}
    )


def edit_watchlist(request, pk):
    """
    View: Adds or removes current auction to/from the watchlist.
    """
    if request.method == "POST":
        auction = Listing.objects.get(pk=pk)
        if (
            Watchlist.objects.all()
            .filter(user=request.user)
            .filter(auction=auction)
            .exists()
            == False
        ):
            new_watchlist = Watchlist.objects.create(auction=auction, user=request.user)
        else:
            Watchlist.objects.filter(user=request.user).filter(auction=auction).delete()

    url = reverse("auction", kwargs={"pk": pk})
    return HttpResponseRedirect(url)


def close_listing(request, pk):
    """
    View: Closes a listed auction by setting its "active" attribute to False
    """
    if request.method == "POST":
        auction = Listing.objects.get(pk=pk)
        if request.user == auction.user:
            auction.active = False
            auction.save(update_fields=["active"])
    url = reverse("auction", kwargs={"pk": pk})
    return HttpResponseRedirect(url)


class CommentForm(ModelForm):
    """
    Form: Make a comment
    """

    class Meta:
        model = Comment
        fields = ["comment"]

def make_comment(request, pk):
    comment_form = CommentForm(request.POST)

    if comment_form.is_valid():
        auction = Listing.objects.get(pk=pk)
        user = request.user
        comment = comment_form.save(commit=False)
        
