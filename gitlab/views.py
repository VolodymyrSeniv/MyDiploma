from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import generic
from gitlab.models import Classroom, Assignment


# Create your views here.
def index(request: HttpResponse) -> HttpResponse:
    return render(request, "gitlab/index.html")


#this is a classbased representation of a classrooms
class ClassroomsListView(generic.ListView):
    model = Classroom
    queryset = Classroom.objects.select_related("teacher").prefetch_related("students")
    #above i am fixing n+1 problem by using select_related and prefetch_related
    paginate_by = 5

class ClassroomsDetailView(generic.DetailView):
    model = Classroom


#this is a classbased representation of assignments
class AssignmentsListView(generic.ListView):
    model = Assignment
    queryset = Assignment.objects.select_related("classroom", "classroom__teacher").prefetch_related("classroom__students")
    #above i am fixing n+1 problem i should fix it later
    paginate_by = 10

class AssignmentsDetailView(generic.DetailView):
    model = Assignment