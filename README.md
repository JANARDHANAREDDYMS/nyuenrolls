# NYU Enrolls

NYU Enrolls is a modern course enrollment application designed to address the challenges faced by NYU students, faculty, and administrators. It streamlines the registration process, ensures accurate course availability, and provides an intuitive user experience.

## Project Overview

**Goal**: Simplify and enhance the course enrollment experience at NYU by addressing pain points such as inaccurate course availability, limited waitlist visibility, and lack of real-time notifications.

**Target Audience**: NYU students (Master’s and PhD), faculty, and administrative staff.

---

## Features

### MVP (Minimum Viable Product)
- **Course Add/Drop/Swap**: Allows students to easily manage their course registrations.
- **Override Forms**: Enables students to request enrollment in restricted or full courses.
- **User Authentication**: Secure login for students, faculty, and admins.

### MLP (Minimum Lovable Product)
- **Pre-Registration System**: Students can pre-register for courses before the official registration period.
- **Guaranteed Course Enrollment**: Implements a fair system to ensure students get essential courses.
- **Accurate Course Availability**: Displays real-time seat availability with category-based allocation.
- **Category-Based Seat Allocation**: Allocates seats based on student categories (e.g., Master’s, PhD).
- **Modern User Interface**: Provides a seamless, user-friendly experience.
- **Capacity Alert Notifications**: Notifies students of seat availability in real-time.

### Nice-to-Have Features
- **Detailed Analytics & Reports**: Insights into enrollment trends for administrators.
- **Course Recommendation Engine**: Suggests courses based on student preferences and history.
- **Mobile Application Version**: On-the-go access for students.

---

## Team Members

| Name             | Role               |
|------------------|--------------------|
| Alper Mumcular   | Product Owner      |
| [Team Member 1]  | Developer          |
| [Team Member 2]  | Developer          |
| [Team Member 3]  | UI/UX Designer     |
| [Team Member 4]  | QA Engineer        |

---

## Technology Stack

- **Frontend**: React.js
- **Backend**: Django/Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: OAuth 2.0
- **DevOps**: Docker, GitHub Actions

---

## Prerequisites

To run the project, ensure the following are installed:

- Python 3.8 or higher
- Node.js and npm
- PostgreSQL
- Docker (for containerized setup)

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo-url>.git
   cd nyu-enrolls
   ```

2. Backend Setup:
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate # On Windows: .\env\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. Frontend Setup:
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. Access the application:
   - Backend: `http://127.0.0.1:8000/`
   - Frontend: `http://localhost:3000/`

---

## Development Workflow

- **Version Control**: Git is used for versioning. Follow the branch naming convention: `feature/<name>` or `bugfix/<name>`.
- **Code Review**: All pull requests require review by at least one team member.
- **Issue Tracking**: Use GitHub Issues to track bugs, enhancements, and feature requests.

### Running Tests

1. Backend tests:
   ```bash
   python manage.py test
   ```

2. Frontend tests:
   ```bash
   npm test
   ```

---

## Deployment

### Using Docker

1. Build and run containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   ```
   http://localhost:8000/  # Backend
   http://localhost:3000/  # Frontend
   ```

---

## Contribution Guidelines

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/<your-feature-name>
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your fork and submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or suggestions, please reach out to [your email/contact info].

---

We hope NYU Enrolls transforms the course registration process into a seamless experience for everyone at NYU! 🚀
