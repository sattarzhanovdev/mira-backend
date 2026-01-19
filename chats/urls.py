from django.urls import path
from .views import TripListCreateView, TripChatView

urlpatterns = [
    path("trips/", TripListCreateView.as_view()),
    path("trips/<int:trip_id>/chat/", TripChatView.as_view()),
]
