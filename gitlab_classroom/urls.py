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
                          AssignmentDeleteView,
                          StudentsListView,
                          StudentsDetailView,
                          StudentCreateView,
                          StudentUpdateView,
                          StudentDeleteView)


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
    path("classrooms/<int:pk>/delete/", ClassroomDeleteView.as_view(), name="classroom-delete"),
    path("students/", StudentsListView.as_view(), name="student-list"),
    path("students/<int:pk>/", StudentsDetailView.as_view(), name="student-detail"),
    path("students/create/", StudentCreateView.as_view(), name="student-create"),
    path("students/<int:pk>/update/", StudentUpdateView.as_view(), name="student-update"),
    path("students/<int:pk>/delete/", StudentDeleteView.as_view(), name="student-delete"),
]


app_name = "gitlab_classroom" 