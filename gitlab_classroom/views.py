from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.forms import DateTimeInput
from gitlab_classroom.forms import ClassroomSearchForm, AssignmentSearchForm
from gitlab_classroom.models import Classroom, Assignment
from gitlab_classroom.forms import AssignmentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
import gitlab


# Create your views here.
@login_required
def index(request: HttpResponse) -> HttpResponse:
    return render(request, "gitlab_classroom/index.html")


#this is a classbased representation of a classrooms
class ClassroomsListView(LoginRequiredMixin, generic.ListView):
    model = Classroom
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ClassroomsListView, self).get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["search_form"] = ClassroomSearchForm(
            initial={"title": title}
        )
        return context

    def get_queryset(self):
        queryset = Classroom.objects.select_related("teacher").prefetch_related("students").filter(teacher=self.request.user)
        form = ClassroomSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(title__icontains=form.cleaned_data["title"])
        """Override to filter assignments to those owned by the current user."""
        return queryset


class ClassroomsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Classroom


class ClassroomCreateView(LoginRequiredMixin, generic.CreateView):
    model = Classroom
    fields = ["title", "description", "organization"]
    success_url = reverse_lazy("gitlab_classroom:classroom-list")
    template_name = "gitlab_classroom/classroom_form.html"
    
    def form_valid(self, form):
        # Call the superclass method to save the Classroom object
        user = self.request.user
        form.instance.teacher = user
        response = super().form_valid(form)
        # Configure access to your GitLab instance
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        
        # Create a new GitLab group with the classroom title
        group_data = {'name': self.object.title,
                      'path': self.object.title.replace(" ", "_").lower(),
                      'description':self.object.description}
        group = gl.groups.create(group_data)
    
        # Optionally save GitLab group ID to Classroom object for further reference
        # self.object.gitlab_group_id = group.id
        # self.object.save()
        self.object.gitlab_id = group.id
        self.object.save()
        return response
    #connect to gitlab functionality


class ClassroomUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Classroom
    fields = ["title", "description", "organization"]
    success_url = reverse_lazy("gitlab_classroom:classroom-list")
    template_name = "gitlab_classroom/classroom_form.html"
    #connect to gitlab functionality

    def form_valid(self, form):
        # This method is called when the form is valid, before saving the object.
        # Here you can include your logic to update GitLab group or other details.
        
        # Access the current user
        user = self.request.user
        
        # Optionally, access the GitLab ID stored in the Classroom instance
        gitlab_group_id = form.instance.gitlab_id
        
        # Example: update a GitLab group's name or other details
        # Configure access to your GitLab instance
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        
        group = gl.groups.get(gitlab_group_id)
        # Assuming you want to update the name of the group based on a field in your form
        group.name = form.cleaned_data['title']
        group.description = form.cleaned_data['description']
        group.save()
        # Don't forget to save the form and the instance it represents
        response = super().form_valid(form)
        
        return response


class ClassroomDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Classroom
    template_name = "gitlab_classroom/classroom_confirm_delete.html"
    success_url = reverse_lazy("gitlab_classroom:classroom-list")

    def form_valid(self, form):
        # Get the object
        user = self.request.user
        self.object = self.get_object()
        response = super().form_valid(form)
        # Optionally retrieve GitLab group ID from Classroom object
        gitlab_group_id = self.object.gitlab_id
        # Configure access to your GitLab instance
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        # Delete the GitLab group
        group = gl.groups.get(gitlab_group_id)
        group.delete()
        
        return response


#this is a classbased representation of assignments
class AssignmentsListView(LoginRequiredMixin, generic.ListView):
    model = Assignment
    queryset = Assignment.objects.select_related("classroom", "classroom__teacher").prefetch_related("classroom__students")
    #above i am fixing n+1 problem i should fix it later
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssignmentsListView, self).get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["search_form"] = AssignmentSearchForm(
            initial={"title": title}
        )
        return context

    def get_queryset(self):
        queryset = Assignment.objects.select_related("classroom", "classroom__teacher").prefetch_related("classroom__students").filter(teacher=self.request.user)
        form = AssignmentSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(title__icontains=form.cleaned_data["title"])
        """Override to filter assignments to those owned by the current user."""
        return queryset


class AssignmentsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Assignment


class AssignmentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Assignment
    form_class = AssignmentForm
    success_url = reverse_lazy("gitlab_classroom:assignment-list")
    template_name="gitlab_classroom/assignment_form.html"

    def form_valid(self, form):
        user = self.request.user
        form.instance.teacher = user
        classroom = get_object_or_404(Classroom, pk=self.kwargs.get('pk'))
        form.instance.classroom = classroom 
        response = super().form_valid(form)
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)

        # Ensure the Classroom has a linked GitLab group
        if classroom.gitlab_id:
            # Create a project within the Classroom's GitLab group
            project_data = {
                'name': form.instance.title,
                'description': form.instance.description,
                'namespace_id': classroom.gitlab_id  # This assigns the project to the group
            }
            project = gl.projects.create(project_data)
            
            # Optionally save GitLab project ID to Assignment object for further reference
            # form.instance.gitlab_project_id = project.id
            # form.instance.save()
            self.object.gitlab_id = project.id
            self.object.save()
        
        return response


class AssignmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Assignment
    form_class = AssignmentForm
    success_url=reverse_lazy("gitlab_classroom:assignment-list")
    template_name="gitlab_classroom/assignment_form.html"

    def form_valid(self, form):
        user = self.request.user
        gitlab_project_id = form.instance.gitlab_id
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        project = gl.projects.get(gitlab_project_id)
        project.name = form.cleaned_data["title"]
        project.description = form.cleaned_data["description"]
        project.save()

        response = super().form_valid(form)
        return response 


class AssignmentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Assignment
    template_name = "gitlab_classroom/assignment_confirm_delete.html"
    success_url = reverse_lazy("gitlab_classroom:assignment-list")

    def form_valid(self, form):
        user = self.request.user
        self.object = self.get_object()
        response = super().form_valid(form)
        gitlab_assignment_id = self.object.gitlab_id
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        project = gl.projects.get(gitlab_assignment_id)
        project.delete()

        return response
