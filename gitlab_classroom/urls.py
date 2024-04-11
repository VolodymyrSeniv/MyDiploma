from django.urls import path
from gitlab_classroom.views import (index,
                          ClassroomsListView,
                          AssignmentsListView,
                          ClassroomsDetailView,
                          AssignmentsDetailView,
                          ClassroomCreateView,
                          ClassroomUpdateView,
                          ClassroomDeleteView,
                          AssignmentCreateView,
                          AssignmentUpdateView,
                          AssignmentDeleteView)


urlpatterns = [
    path("", index, name="index"),
    path("classrooms/", ClassroomsListView.as_view(), name="classroom-list"),
    path("assignments/", AssignmentsListView.as_view(), name="assignment-list"),
    path("classrooms/<int:pk>/", ClassroomsDetailView.as_view(), name="classroom-detail"),
    path("assignments/<int:pk>/", AssignmentsDetailView.as_view(), name="assignment-detail"),
    path("classrooms/<int:pk>/assignments/create/", AssignmentCreateView.as_view(), name="assignment-create"),
    path("assignments/<int:pk>/update/", AssignmentUpdateView.as_view(), name="assignment-update"),
    path("assignments/<int:pk>/delete/", AssignmentDeleteView.as_view(), name="assignment-delete"),
    path("classrooms/create/", ClassroomCreateView.as_view(), name="classroom-create"),
    path("classrooms/<int:pk>/update/", ClassroomUpdateView.as_view(), name="classroom-update"),
    path("classrooms/<int:pk>/delete/", ClassroomDeleteView.as_view(), name="classroom-delete")
]


app_name = "gitlab_classroom" 