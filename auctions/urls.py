from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auction/<int:id>", views.auction, name="auction"),
    path("categories", views.categories, name='categories'),
    path("categories/<str:category>", views.category_listing, name='category'),
    path("closed", views.closed_auctions, name='closed_auctions'),

]

urlpatterns +=  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
