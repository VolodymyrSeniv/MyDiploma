from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import generic
from gitlab_classroom.models import Classroom, Assignment
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
@login_required
def index(request: HttpResponse) -> HttpResponse:
    return render(request, "gitlab_classroom/index.html")


#this is a classbased representation of a classrooms
class ClassroomsListView(LoginRequiredMixin, generic.ListView):
    model = Classroom
    queryset = Classroom.objects.select_related("teacher").prefetch_related("students")
    #above i am fixing n+1 problem by using select_related and prefetch_related
    paginate_by = 5

class ClassroomsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Classroom


#this is a classbased representation of assignments
class AssignmentsListView(LoginRequiredMixin, generic.ListView):
    model = Assignment
    queryset = Assignment.objects.select_related("classroom", "classroom__teacher").prefetch_related("classroom__students")
    #above i am fixing n+1 problem i should fix it later
    paginate_by = 10

class AssignmentsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Assignment