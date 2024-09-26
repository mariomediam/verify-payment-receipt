from django.urls import path
from .views import HomeView, ExtractTextView


urlpatterns= [
    # path("inicio/", HomeView.as_view()),
    path("", HomeView.as_view()),
    path("extract-text/", ExtractTextView.as_view()),
]
