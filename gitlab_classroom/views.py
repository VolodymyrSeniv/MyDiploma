from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import generic
from gitlab_classroom.forms import (ClassroomSearchForm,
                                    AssignmentSearchForm,
                                    StudentSearchForm,
                                    AddStudentToClassroomForm,
                                    ForkProjectsForm)
from gitlab_classroom.models import Classroom, Assignment, Student
from gitlab_classroom.forms import AssignmentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
import gitlab


# Create your views here.
@login_required
def index(request: HttpResponse) -> HttpRequest:
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
    context_object_name = 'classroom'
    template_name = 'gitlab_classroom/classroom_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom_id = self.kwargs.get('pk')
        context['add_student_form'] = AddStudentToClassroomForm(classroom_id=classroom_id)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Get the current classroom object
        classroom_id = self.kwargs.get('pk')  # Get classroom ID from URL

        if 'add_student' in request.POST:
            add_form = AddStudentToClassroomForm(request.POST, classroom_id=classroom_id)
            if add_form.is_valid():
                user = self.request.user
                gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
                group = gl.groups.get(self.object.gitlab_id)
                subgroups = group.subgroups.list(all=True)
                members_group = gl.groups.get(subgroups[1].id)
                student = add_form.cleaned_data['student']
                if subgroups:
                    member = members_group.members.create({'user_id': student.gitlab_id,
                                                          'access_level': gitlab.const.DEVELOPER_ACCESS})
                self.object.students.add(student)
                return HttpResponseRedirect(self.object.get_absolute_url())
            else:
                # Log form errors to help debug
                print(add_form.errors)

        elif 'remove_student' in request.POST:
            student_id = request.POST.get('student_id')
            if student_id:
                user = self.request.user
                gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
                group = gl.groups.get(self.object.gitlab_id)
                subgroups = group.subgroups.list(all=True)
                members_group = gl.groups.get(subgroups[1].id)
                student = get_object_or_404(Student, id=student_id)
                member = members_group.members.get(student.gitlab_id)
                member.delete()
                self.object.students.remove(student)
                return HttpResponseRedirect(self.object.get_absolute_url())

        return self.render_to_response(self.get_context_data())



class ClassroomCreateView(LoginRequiredMixin, generic.CreateView):
    model = Classroom
    fields = ["title", "description", "organization"]
    success_url = reverse_lazy("gitlab_classroom:classroom-list")
    template_name = "gitlab_classroom/classroom_form.html"
    
    def form_valid(self, form):
        user = self.request.user
        form.instance.teacher = user
        response = super().form_valid(form)

        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)

        group_data = {
            'name': self.object.title,
            'path': self.object.title.lower(),
            'description': self.object.description
        }
        group = gl.groups.create(group_data)

        # Create members and assignments subgroups
        def create_subgroup(name_suffix, description):
            subgroup_path = f"{group_data["path"]}_{name_suffix}"
            subgroup_data = {
                "name": name_suffix,
                "path": subgroup_path,
                "description": description,
                "parent_id": group.id
            }
            return gl.groups.create(subgroup_data)

        members = create_subgroup("MEMBERS", "Classroom Members")
        assignments = create_subgroup("ASSIGNMENTS", "Assignments folder")

        self.object.gitlab_id = group.id
        self.object.save() 
        return response


class ClassroomUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Classroom
    fields = ["title", "description", "organization"]
    success_url = reverse_lazy("gitlab_classroom:classroom-list")
    template_name = "gitlab_classroom/classroom_form.html"
    #connect to gitlab functionality

    def form_valid(self, form):
        # This method is called when the form is valid, before saving the object.
        
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
        if gitlab_group_id:
            # Configure access to your GitLab instance
            gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
            # Delete the GitLab group
            group = gl.groups.get(gitlab_group_id)
            group.delete()
        
        return response


class StudentsListView(LoginRequiredMixin, generic.ListView):
    model = Student
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StudentsListView, self).get_context_data(**kwargs)
        gitlab_username = self.request.GET.get("gitlab_username", "")
        context["search_form"] = StudentSearchForm(
            initial={"gitlab_username" : gitlab_username}
        )
        return context
    
    def get_queryset(self):
        queryset = Student.objects.all()
        form = StudentSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(gitlab_username__icontains=form.cleaned_data["gitlab_username"])


class StudentsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Student


class StudentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Student
    fields = ["gitlab_username",
              "first_name",
              "second_name",
              "email"]
    success_url = reverse_lazy("gitlab_classroom:student-list")
    template_name = "gitlab_classroom/student_form.html"

    def form_valid(self, form):
        user = self.request.user
        response = super().form_valid(form)

        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        try:
        # Retrieve the user by username
            students = gl.users.list(username=self.object.gitlab_username)  # Replace 'desired_username' with the actual username
            if students:
                student = students[0]  # Assuming the username is unique and the first result is the desired one
                print("User ID:", student.id)
                print("Username:", student.username)
            else:
                print("No user found with that username.")
        except Exception as e:
            print("An error occurred:", e)
        self.object.gitlab_id = student.id
        self.object.save()
        return response


class StudentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Student
    fields = {"gitlab_id", "gitlab_username", "first_name", "second_name", "email"}
    success_url=reverse_lazy("gitlab_classroom:student-list")
    template_name="gitlab_classroom/student_form.html"


class StudentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Student
    template_name = "gitlab_classroom/student_confirm_delete.html"
    success_url = reverse_lazy("gitlab_classroom:student-list")


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fork_projects_form"] = ForkProjectsForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ForkProjectsForm(request.POST)
        user = self.request.user
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        # assignment = self.get_object()
        assignment_id = self.kwargs.get('pk')
        assignment = Assignment.objects.get(pk=assignment_id)
        if form.is_valid():
            gitlab_template_id = form.cleaned_data['gitlab_template_id']
            # Dummy IDs for the assignments_group and students_group
            assignments_group = gl.groups.get(assignment.gitlab_id)  # Ensure you have this attribute or fetch it appropriately
            # classroom_gitlab_id = assignment.classroom.gitlab_id
            classroom_group = gl.groups.get(assignment.classroom.gitlab_id)
            #assignments_group = self.create_or_get_subgroup(classroom_group, 'ASSIGNMENTS')
            members_group = self.create_or_get_subgroup(classroom_group, 'MEMBERS')
            self.fork_project_for_students(assignments_group, gitlab_template_id, members_group)
            # students_group = gl.groups.get(assignment.students_group_id)  # Ensure you have this attribute or fetch it appropriately
        context = self.get_context_data()
        context['fork_projects_form'] = form
        return HttpResponseRedirect(self.object.get_absolute_url())
        # return render(request, None, context)

    def create_or_get_subgroup(self, parent_group, subgroup_name):
        user = self.request.user
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        """ Create a subgroup if it does not exist or return existing one """
        subgroups = parent_group.subgroups.list(all=True)
        for subgroup in subgroups:
            if subgroup.name == subgroup_name:
                return gl.groups.get(subgroup.id)

        subgroup_data = {
            'name': subgroup_name,
            'path': subgroup_name,
            'parent_id': parent_group.id
        }
        return gl.groups.create(subgroup_data)

    def fork_project_for_students(self, assignments_group, base_project_id, student_group):
        user = self.request.user
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        students = gl.groups.get(student_group.id).members.list(all=True)
        base_project = gl.projects.get(base_project_id)
        #main algorythm for creating subgroups for eachstudent and project forking is below
        for student in students:
            if int(student.id) != int(user.gitlab_id):  # Assuming 'gitlab_id' is the attribute holding the GitLab user ID
                personal_group_name = f"{assignments_group.name}_{student.username}"
                student_subgroup = self.create_or_get_subgroup(assignments_group, personal_group_name)
                forked_project_data = base_project.forks.create({
                    'namespace': student_subgroup.id,
                    'name': f"{personal_group_name}_project",
                    'path': f"{personal_group_name}_project"
                })
                forked_project = gl.projects.get(forked_project_data.id)

                    # Add the student to the forked project with Developer access
                forked_project.members.create({
                    'user_id': student.id,
                    'access_level': gitlab.const.AccessLevel.DEVELOPER
                })
                print(f"Project forked for {student.username} in subgroup {personal_group_name}")



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
            group = gl.groups.get(classroom.gitlab_id)
            subgroups = group.subgroups.list(all=True)
            assignments_group = gl.groups.get(subgroups[0].id)
            # Create a project within the Classroom's GitLab group
            subgroup_data = {
                "name": form.instance.title,
                "path": f"{assignments_group.name}_{form.instance.title}",
                "description": form.instance.description,
                "parent_id": assignments_group.id  # This assigns the project to the group
            }
            group = gl.groups.create(subgroup_data)
            
            # Optionally save GitLab project ID to Assignment object for further reference
            # form.instance.gitlab_project_id = project.id
            # form.instance.save()
            self.object.repo_url = group.web_url
            self.object.gitlab_id = group.id
            self.object.save()
        
        return response


class AssignmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Assignment
    form_class = AssignmentForm
    success_url=reverse_lazy("gitlab_classroom:assignment-list")
    template_name="gitlab_classroom/assignment_form.html"

    def form_valid(self, form):
        user = self.request.user
        gitlab_group_id = form.instance.gitlab_id
        gl = gitlab.Gitlab('https://gitlab-stud.elka.pw.edu.pl', private_token=user.access_token)
        group = gl.groups.get(gitlab_group_id)
        group.name = form.cleaned_data["title"]
        group.description = form.cleaned_data["description"]
        group.save()

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
        group = gl.groups.get(gitlab_assignment_id)
        group.delete()

        return response
