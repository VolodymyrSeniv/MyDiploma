from django.urls import path
from gitlab.views import (index,
                          ClassroomsListView,
                          AssignmentsListView,
                          ClassroomsDetailView,
                          AssignmentsDetailView)


urlpatterns = [
    path("", index, name="index"),
    path("classrooms/", ClassroomsListView.as_view(), name="classroom-list"),
    path("assignments/", AssignmentsListView.as_view(), name="assignment-list"),
    path("classrooms/<int:pk>/", ClassroomsDetailView.as_view(), name="classroom-detail"),
    path("assignments/<int:pk>/", AssignmentsDetailView.as_view(), name="assignment-detail")
]


app_name = "gitlab"