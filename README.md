SecureTask API
SecureTask API is a production ready backend service built with FastAPI, PostgreSQL, Docker, and Microsoft Azure. The project demonstrates secure authentication, containerization, CI/CD automation, and real world cloud deployment practices.

Live Deployment
Swagger Documentation
https://securetaskapi-app-bnbybwgdhvhkhefd.eastus-01.azurewebsites.net/docs

Overview
This project was designed to simulate a real world backend system with authentication, role based authorization, database integration, and automated deployment to the cloud.
It showcases backend engineering fundamentals and infrastructure level deployment skills rather than just local development.

Features
JWT authentication
Role based access control
Secure password hashing
PostgreSQL database integration
SQLAlchemy ORM
Docker containerization
Azure Container Registry integration
Azure App Service deployment
GitHub Actions CI/CD automation
Environment variable based configuration

Architecture
Client requests are handled by a FastAPI application.
The application communicates with PostgreSQL using SQLAlchemy and psycopg.
The application runs inside a Docker container.
The container image is pushed to Azure Container Registry.
Azure App Service pulls and runs the container image in production.
GitHub Actions automates build and deployment on every push to the main branch.

Tech Stack
Backend
Python
FastAPI
SQLAlchemy
psycopg

Database
Azure PostgreSQL Flexible Server

Cloud and DevOps
Docker
Azure Container Registry
Azure App Service
GitHub Actions

Security
JWT
Password hashing
Role based authorization
Environment variable configuration

Local Development Setup
Clone the repository
git clone https://github.com/Learnlife001/securetask-api.git
cd securetask-api

Create virtual environment
python -m venv .venv
..venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Run locally
uvicorn app.main:app –reload

CI/CD Pipeline
On every push to the main branch:
1. GitHub Actions builds the Docker image
2. The image is pushed to Azure Container Registry
3. Azure App Service pulls the updated image
4. The API is automatically redeployed
This ensures automated and consistent production deployments.

Production Lessons Learned
Misconfigured environment variables can break production authentication
Cloud database authentication requires strict configuration
Container based deployment improves portability and reliability
CI/CD automation eliminates manual deployment errors
Logging and monitoring are critical for debugging production systems

Future Improvements
Refresh token implementation
Rate limiting
Admin dashboard
Redis caching
Monitoring and alerting integration
  
Author
Chigozie Okuma
GitHub: https://github.com/Learnlife001
LinkedIn: https://www.linkedin.com/in/cjokuma23/
Portfolio: https://learnlife-portfolio.vercel.app/
