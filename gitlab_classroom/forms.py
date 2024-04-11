from django import forms
from gitlab_classroom.models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        # It's important to specify the input format if you're using a custom format
        input_formats = ['%Y-%m-%dT%H:%M']


class ClassroomSearchForm(forms.Form):
    title = forms.CharField(max_length=255,
                            required=False,
                            label="",
                            widget=forms.TextInput(
                                attrs={
                                    "placeholder": "Search by title"
                                }
                            )
                        )


class AssignmentSearchForm(forms.Form):
    title = forms.CharField(max_length=255,
                            required=False,
                            label="",
                            widget=forms.TextInput(
                                attrs={
                                    "placeholder": "search by title"
                                }
                            )
                        )