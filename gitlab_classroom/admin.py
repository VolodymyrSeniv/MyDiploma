from django.contrib import admin
from gitlab_classroom.models import Teacher, Classroom, Assignment, Student, Submission
from django.contrib.auth.admin import UserAdmin

# admin.site.register(Teacher, UserAdmin)
# admin.site.register(Classroom)
admin.site.register(Student)

@admin.register(Teacher)
class TeacherAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("gitlab_id", "access_token", )
    fieldsets = UserAdmin.fieldsets + (("Gitlab Information", {"fields": ("gitlab_id", "access_token", )}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Gitlab Information", {"fields": ("gitlab_id", "access_token", )}),)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["title", "creation_date", "organization", "teacher", ]
    list_filter = ["teacher", ]
    search_fields = ["title", ]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["title", "creation_date", "deadline", "teacher", "classroom", ]
    list_filter = ["teacher", "creation_date", ]
    search_fields = ["title", ]