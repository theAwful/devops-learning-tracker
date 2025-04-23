# Secure DevSecOps Learning Tracker

A Dockerized web app to track and gamify DevSecOps learning, built with Flask, PostgreSQL, Docker, GitHub Actions, and Chart.js. Features a resource library, goal tracker, project log, gamification, visualizations, and secure CI/CD, aligned with a 12-month DevSecOps learning plan.

## Setup
1. Install Docker and Python 3.9.
2. Clone the repo: `git clone <your-repo-url>`
3. Run: `docker-compose up --build`
4. Access at `http://localhost:5000`
5. Register a user and start tracking!

## Features
- **Resource Library**: Store, tag, and search learning materials.
- **Goal Tracker**: Set and track goals with progress, deadlines, and points.
- **Project Log**: Document hands-on projects with repo links.
- **Gamification**: Earn points and unlock milestones (e.g., “Docker Pro”).
- **Dashboard**: Visualize progress with bar and line charts.
- **Security**: Input sanitization, password hashing, CI/CD scans (Semgrep, Trivy).
- **Export/Import**: Backup or share data as JSON.

## Security Measures
- Sanitizes inputs with Bleach to prevent XSS.
- Uses bcrypt for password hashing.
- Secure sessions with Flask-Login.
- CI/CD pipeline with Semgrep and Trivy scans.

## CI/CD
- GitHub Actions automates testing, Semgrep scans, Trivy scans, and Docker Hub pushes.
- Set `DOCKER_USERNAME` and `DOCKER_PASSWORD` in GitHub Secrets.

## Syllabus
- **Month 1–2**: Git, Docker (e.g., “Dockerize a Flask app”).
- **Month 3–4**: CI/CD, GitHub Actions (e.g., “Set up CI/CD pipeline”).
- **Month 5–6**: Security Tools (e.g., “Run Semgrep”).
- **Month 7–8**: Kubernetes, Terraform (e.g., “Deploy a pod”).
- **Month 9–12**: Cloud, Certifications (e.g., “Pass CKA exam”).
