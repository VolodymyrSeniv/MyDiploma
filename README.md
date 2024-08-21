# GitLab Classroom Application - Setup and Run Instructions

The **GitLab Classroom application** is a full-stack web tool developed as part of my thesis. It is designed to improve the management of classroom activities, assignments, and the assessment of student projects, labs, and tasks for teachers and professors of the Faculty of Electronics and Information Sciences at the Warsaw University of Technology.

By utilizing the powerful version control and project management functions of GitLab, along with the GitLab API, this application helps address the challenges of managing and evaluating assignments, providing timely feedback, and facilitating collaboration in programming projects.

## Prerequisites

Before running the GitLab Classroom application, make sure you have the following installed on your system:

1. **Python 3.8+**: You can download Python from [python.org](https://www.python.org/downloads/).
2. **Git**: Ensure Git is installed to clone the repository. You can download it from [git-scm.com](https://git-scm.com/downloads).
3. **Virtualenv**: It's recommended to use a virtual environment for managing dependencies. You can install it using:
   ```bash
   pip install virtualenv

##Setting Up the Environment

1. **Create a virtual environment**: virtualenv venv
2. **Activate the virtual environment**:
   *Windows*: venv\Scripts\activate
   *macOS/Linux*: source venv/bin/activate
4. **Install the required dependencies using pip**: pip install -r requirements.txt
5. **Apply the migrations to set up the database**: python manage.py migrate
6. **(Optional) If you want to load initial data, use**: python manage.py loaddata initial_data.json
7. **Start the Django development server**: python manage.py runserver
8. **Open your web browser and navigate to http://127.0.0.1:8000/ to access the application**.
