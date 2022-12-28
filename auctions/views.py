from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse



from .models import User, Auction, Bids, Categories, Comments


def comment_to_list(comments):
    mainlist = []
    thread = []

    for comment in comments:
        if comment.subcomment == None:
            thread.append(comment)
            for subcomment in comment.subcomments.all():
                thread.append(subcomment)
        
            mainlist.append(thread)
            thread = []

    return mainlist        
    

def index(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": auctions,
    })

def auction(request, id):
    auction = Auction.objects.get(pk=id)
    #Ordering the bids by highest to lowest
    bids = auction.bids.all().order_by('-amount')
    #Manually adjusting image url
    img = '../' + str(auction.image)
    comments = auction.comments.all()

    comment_list = comment_to_list(comments)

    return render(request, "auctions/auction.html",{
        "auction": auction,
        "img": img,
        "bids": bids,
        "comments": comment_list,
    })

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
