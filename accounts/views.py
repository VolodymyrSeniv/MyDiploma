import gitlab
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


# Create your views here.
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "accounts/login.html")
    elif request.method == "POST":
        gitlab_id = request.POST["gitlab_id"]
        access_token=request.POST["access_token"]
        gl = gitlab.Gitlab(url='https://gitlab-stud.elka.pw.edu.pl', private_token=access_token)
        try:
            gl.auth()
            print("You are logged in to GitLab.")
            user = authenticate(gitlab_id=gitlab_id, access_token=access_token)
            gl_user = gl.user
            print(f"GitLab User ID: {gl_user.id}")
            print(f"GitLab User username: {gl_user.username}")
            print(f"GitLab User name: {gl_user.name}")
            print(f"GitLab User name: {gl_user.avatar_url}")
            print(f"GitLab User name: {gl_user.web_url}")
            if user:
                user.first_name = gl_user.name
                print(f"This {user.first_name}")
                login(request, user)
                return HttpResponseRedirect(reverse("gitlab_classroom:index"))
            else:
                error_context = {
                    "error": "Invalid credentials" 
                }
        except gitlab.exceptions.GitlabAuthenticationError:
            error_context = {
                "error": "Wrong access token"
            }
        return render(request, "accounts/login.html", context=error_context)

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return render(request, "accounts/logout.html")