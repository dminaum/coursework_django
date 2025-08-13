from django.urls import path
from .views import (
    ClientListView, ClientDetailView,
    ClientCreateView, ClientUpdateView,
    ClientDeleteView, AttemptView, AttemptDetailView, MessageListView, MessageDetailView, MessageCreateView,
    MessageUpdateView, MessageDeleteView, MailingListView, MailingCreateView, MailingDetailView, MailingUpdateView,
    MailingDeleteView, MailingSendNowView
)
from .views.stats import StatsView

app_name = 'mailings'

urlpatterns = [
    path('attempts/list/', AttemptView.as_view(), name='attempt_list'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt_detail'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('', MailingListView.as_view(), name='mailing_list'),
    path('create/', MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('<int:pk>/send/', MailingSendNowView.as_view(), name='mailing_send'),
    path('stats/', StatsView.as_view(), name='stats'),
]
