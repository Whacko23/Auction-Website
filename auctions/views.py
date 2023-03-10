from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from datetime import date

#NOTE: Server Side Validation Skipped/ Too Much Work for non-production site

#TODO Close the auction based on allotted_time
#TODO Test: Close auction -> Update Winner


from .models import User, Auction, Bids, Categories, Comments, Watchlist

# Helper functions
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
    
def get_watchlist(req_user):
    watchlist_queryset = Watchlist.objects.filter(user=req_user)
    
    watchlist =[]

    #Converting watchlist queryset to auction list
    for item in watchlist_queryset:
        # Manually adjusting image url
        item.auction.image = '../' + str(item.auction.image)
        watchlist.append(item.auction)

    return watchlist

def file_upload(request, field_name, location=''):
    myfile = request.FILES[field_name]
    fs = FileSystemStorage()

    filename = fs.save(location + myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    
    return uploaded_file_url

def get_year_month():
    return str(date.today().year) + '/' + str(date.today().month) + '/'

def get_won_auctions(request_user):
    return Auction.objects.filter(winner=request_user)

# Webpage Views

def index(request):
    auctions = Auction.objects.filter(closed=False)
    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []
    
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "watchlist": watchlist,
        "title": 'Active Listing',
        "won_auctions": won_auctions,


    })

def auction(request, id):
    message = ''
    green_message = ''
    item_in_watchlist = False
    current_auction = Auction.objects.get(pk=id)

    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    #Ordering the bids by highest to lowest
    bids = current_auction.bids.all().order_by('-amount')
    latest_bid = bids.first() if bids else None

    if bids:
        highest_bid = bids.first().amount
    else :
        highest_bid = 0
        
    if current_auction in watchlist:
        item_in_watchlist = True


    # Add comment
    if request.method == 'POST' and 'comment' in request.POST:
        text = request.POST['comment']
        comment = Comments(user=request.user,comment=text, auction=current_auction)
        comment.save()
        # if comm
    elif request.method == 'POST' and 'anonymous-comment' in request.POST:
        text = request.POST['anonymous-comment']
        comment = Comments(comment=text, auction=current_auction)
        comment.save()
    elif request.method == 'POST' and 'reply' in request.POST:
        text = request.POST['reply']
        parent_id = request.POST['comment_id']
        parent_comment = Comments.objects.get(pk=parent_id)
        comment = Comments(user=request.user,comment=text, auction=current_auction, subcomment=parent_comment)
        comment.save()
    elif request.method == 'POST' and 'anonymous-reply' in request.POST:
        text = request.POST['anonymous-reply']
        parent_id = request.POST['comment_id']
        parent_comment = Comments.objects.get(pk=parent_id)
        comment = Comments(comment=text, auction=current_auction, subcomment=parent_comment)
        comment.save()
    elif request.method == 'POST' and 'close-auction' in request.POST:
        current_auction.closed = True
        if latest_bid:
            current_auction.winner = latest_bid.created_by
        current_auction.save()
        

    #Manually adjusting image url
    img = '../' + str(current_auction.image)
    comments = current_auction.comments.all()

    comment_list = comment_to_list(comments)

    # Add to watchlist
    if request.method=="POST" and 'add_watchlist' in request.POST:
        new_watchlist_item = Watchlist(user=request.user, auction=Auction.objects.get(pk=id))
        if not item_in_watchlist:
            new_watchlist_item.save()

            return HttpResponseRedirect(reverse('auction', kwargs={
                'id': id,
            }))
        else:
            message = "Item already in the watchlist"
            return render(request, "auctions/auction.html",{
                "auction": current_auction,
                "img": img,
                "bids": bids,
                "comments": comment_list,
                "message": message,
                "watchlist": watchlist,
                "watching":item_in_watchlist,
                "won_auctions": won_auctions,

            }) 

    # Remove form wathclist
    if request.method=="POST" and 'remove_watchlist' in request.POST:
        Watchlist.objects.filter(auction=current_auction).delete()
        return HttpResponseRedirect(reverse('auction', kwargs={
            "id":id,
        }))

    if request.method=="POST" and 'bid_amount' in request.POST:
        #IF the user not logged in and wants to bid, redirect to login
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        bid=request.POST["bid_amount"]
        
        # Bid input amount validation
        # IF bid amount is null
        if not bid:
            message = 'Please put a valid amount'
            return render(request, "auctions/auction.html",{
                "auction": current_auction,
                "img": img,
                "bids": bids,
                "comments": comment_list,
                "message": message,
                "watchlist": watchlist,
                "watching":item_in_watchlist,
                "won_auctions": won_auctions,


            }) 

        # IF bid amount is not greater than latest bid
        if int(bid) < int(current_auction.starting_bid):
            message = f'The starting bid is $ {current_auction.starting_bid}. Please bid higher'
            return render(request, "auctions/auction.html",{
                "auction": current_auction,
                "img": img,
                "bids": bids,
                "comments": comment_list,
                "message": message,
                "watchlist": watchlist,
                "watching":item_in_watchlist,
                "won_auctions": won_auctions,

            })
        elif int(bid) < int(highest_bid) + 5:
            message = f'The current bid is $ {highest_bid}. Please bid at least $ {highest_bid + 5}'
            return render(request, "auctions/auction.html",{
                "auction": current_auction,
                "img": img,
                "bids": bids,
                "comments": comment_list,
                "message": message,
                "watchlist": watchlist,
                "watching":item_in_watchlist,
                "won_auctions": won_auctions,

            })            
        else:
        # Save the bid
            bid = Bids(amount=int(bid), posted_by=request.user, auction=current_auction)
            bid.save()

        return HttpResponseRedirect(reverse('auction',kwargs={
            'id':current_auction.id,
        }))


    # Update the current winner after auction expires or closes
    if current_auction.closed and not current_auction.winner:
        if latest_bid.posted_by == request.user:
            current_auction.winner = latest_bid.posted_by
            current_auction.save()
            green_message = "Congratulations! You won the auction"

    # Note, the winner updates only after visiting the closed auction.
    # The winner message is displayed only once

    return render(request, "auctions/auction.html",{
        "auction": current_auction,
        "img": img,
        "bids": bids,
        "comments": comment_list,
        "message": message,
        "green_message": green_message,
        "watchlist": watchlist,
        "watching":item_in_watchlist,
        "won_auctions": won_auctions,


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

def categories(request):
    categories = Categories.objects.all()
    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    return render(request, "auctions/categories.html",{
        "categories": categories,
        "watchlist": watchlist,
        "won_auctions": won_auctions,

    })

def category_listing(request, category):
    category = Categories.objects.get(pk=category)
    auctions = category.auctions.filter(closed=False)
    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    for auction in auctions:
        auction.image = '../' + str(auction.image)


    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "watchlist": watchlist,
        "won_auctions": won_auctions,
        'title': category,

    })

def closed_auctions(request):
    auctions = Auction.objects.filter(closed=True)
    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        'title': 'Closed Auctions', 
        'watchlist': watchlist,
        "won_auctions": won_auctions,

    })

def watchlist(request):
    watchlist = get_watchlist(request.user)   
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    return render(request, "auctions/index.html", {
        "auctions": watchlist,
        "watchlist": watchlist,
        'title': 'Watchlist',
        "won_auctions": won_auctions,

    })

def won_auctions(request):
    watchlist = get_watchlist(request.user)   
    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []

    return render(request, "auctions/index.html", {
        "auctions": won_auctions,
        "watchlist": watchlist,
        'title': 'Won Auctions',
        "won_auctions": won_auctions,

    })

def create_listing(request):

    #Note: Skipped input validation
    if request.method == 'POST':
        name = request.POST["title"]
        price = request.POST["BuyoutPrice"]
        category = request.POST["Category"]
        expiry = request.POST["Expiry-time"]

        imageurl = file_upload(request, "pic", f'images/product/{get_year_month()}')

        new_auction = Auction(name_of_product=name, buyout_price= price, listed_by=request.user, category=Categories.objects.get(pk=category), allotted_time= expiry, image=imageurl)
        new_auction.save()
        return HttpResponseRedirect(reverse('auction', kwargs={
            "id": new_auction.id,
        }))

    won_auctions = get_won_auctions(request.user) if request.user.is_authenticated else []
    watchlist = get_watchlist(request.user) if request.user.is_authenticated else []
    categories = Categories.objects.all()

    return render(request, "auctions/createauction.html",{
        "watchlist": watchlist,
        'categories': categories,
        "won_auctions": won_auctions,

    })
