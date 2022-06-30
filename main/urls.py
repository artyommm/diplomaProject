from django.urls import path
from main import views

urlpatterns = [
    path('', views.index),
    path('sign_up/', views.CreateUser.as_view()),
    path('sign_in/', views.AuthUser.as_view()),
    path('lk/', views.ShowUserLk.as_view()),
    path('change_data/', views.ChangeInducteeData.as_view()),
    path('logout/', views.logout_view),
    path('inductee_list/', views.InducteeList.as_view()),
    path('notifications_list/', views.ShowNotifications.as_view()),
    path('ind_messages/', views.InducteeMessages.as_view()),
    path('add_notification/', views.AddNotification.as_view()),
    path('create_subpoena/', views.CreateSubpoena2.as_view()),
    path('create_message/', views.CreateMessage.as_view()),
    path('subpoenas/', views.ShowSubpoenas.as_view()),
    path('messages/', views.ShowMessages.as_view()),
    path('add_military_id/', views.AddMilitaryID.as_view()),
    path('add_recruiting_office/', views.AddRecruitingOffice.as_view()),
    path('success/', views.success_page_view),
    path('error/', views.error_page_view),
    path('inductee_page/',views.ShowInducteePage.as_view()),
    path('inductee_list/sort/',views.sort_inductee),
    path('success_registration/',views.success_registration_page_view),
]