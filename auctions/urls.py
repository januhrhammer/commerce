from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.category_view, name="categories"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("auction/<str:pk>", views.auction_view, name="auction"),
    path("category/<str:category>", views.category_list, name="category"),
    path("auction/<str:pk>/bid", views.make_bid, name="make_bid"),
    path("auction/<str:user>/watchlist", views.watchlist, name="watchlist"),
    path("auction/<str:pk>/watch", views.edit_watchlist, name="e_watchlist"),
]
