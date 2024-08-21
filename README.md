GitLab Classroom Application - Setup and Run Instructions
The GitLab Classroom application is a full-stack web tool which is developed as part of my thesis, designed to improve the management of classroom activities, assignments and assessment of students projects, labs and tasks for teachers and professors of the Faculty of Electronics and Information Sciences of the Warsaw University of Technology by using the powerful functions of GitLab on version control and project management with the help of GitLab API. In modern education, especially in computer science and software development courses, managing and evaluating student’s assignments can be a difficult task due to the volume of assignments and the number of students, the need for timely feedback, and the importance of collaboration and version control in programming projects. GitLab Classroom solves these problems by providing teachers with an optimized interface for creating classes, assigning assignments, creating projects, tracking student progress, and assessing submitted materials.
Before running the GitLab Classroom application, make sure you have the following installed on your system:
Python 3.8+: You can download Python from python.org.
Git: Ensure Git is installed to clone the repository. You can download it from git-scm.com.
Virtualenv: It's recommended to use a virtual environment for managing dependencies. You can install it using:
pip install virtualenv
Create a virtual environment:
virtualenv venv
Activate the virtual environment:
Windows:
venv\Scripts\activate
macOS/Linux:
source venv/bin/activate
Install the required dependencies using pip:
pip install -r requirements.txt
Apply the migrations to set up the database:
python manage.py migrate
(Optional) If you want to load initial data, use:
python manage.py loaddata initial_data.json
Start the Django development server:
python manage.py runserver
Open your web browser and navigate to http://127.0.0.1:8000/ to access the application.
