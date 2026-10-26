"""Seed dataset generator for Allocate platform

Includes:
- Default Organization: "Acme Consulting Services"
- Users: Maya (Resource Manager), Daniel (Delivery Head), Priya (Team Lead), Alex (Admin)
- 12 Skills across Frontend, Backend, Cloud/DevOps, Architecture/AI
- 40 Employees across 5 roles with varied skills, proficiencies (1-5), and growth targets
- 12 Projects (3 mandatory, 9 optional with profit/growth tradeoffs) with realistic roles and skill requirements
- 6 Employee Leave entries across the 12-week planning horizon
"""

from datetime import date, timedelta
from typing import Dict, Any, List


DEFAULT_ORG_NAME = "Acme Consulting Services"
DEFAULT_START_DATE = date(2026, 11, 2)  # Starting Monday of planning horizon


USERS_DATA = [
    {
        "email": "maya@acmeconsulting.com",
        "full_name": "Maya Lin",
        "role": "resource_manager",
        "password": "password123",
    },
    {
        "email": "daniel@acmeconsulting.com",
        "full_name": "Daniel Vance",
        "role": "delivery_head",
        "password": "password123",
    },
    {
        "email": "priya@acmeconsulting.com",
        "full_name": "Priya Sharma",
        "role": "team_lead",
        "password": "password123",
    },
    {
        "email": "alex@acmeconsulting.com",
        "full_name": "Alex Mercer",
        "role": "admin",
        "password": "password123",
    },
]

SKILLS_DATA = [
    # Frontend
    {"name": "React", "category": "Frontend", "description": "Modern React with hooks and state management"},
    {"name": "TypeScript", "category": "Frontend", "description": "Typed JavaScript development"},
    {"name": "Next.js", "category": "Frontend", "description": "Full-stack React framework"},
    {"name": "React Native", "category": "Frontend", "description": "Cross-platform mobile development"},
    # Backend
    {"name": "Python", "category": "Backend", "description": "Python web frameworks and scripting"},
    {"name": "FastAPI", "category": "Backend", "description": "High performance async Python APIs"},
    {"name": "Go", "category": "Backend", "description": "Concurrent backend services in Golang"},
    {"name": "PostgreSQL", "category": "Backend", "description": "Relational database modeling and query tuning"},
    # Cloud & DevOps
    {"name": "Docker & K8s", "category": "Cloud & DevOps", "description": "Containerization and container orchestration"},
    {"name": "AWS Cloud", "category": "Cloud & DevOps", "description": "Cloud infrastructure, serverless, and VPC networking"},
    # Architecture & AI
    {"name": "System Design", "category": "Architecture & AI", "description": "Distributed systems, scalability, and microservices"},
    {"name": "Machine Learning", "category": "Architecture & AI", "description": "PyTorch, scikit-learn, LLMs, and model serving"},
]

# 40 Employees across 5 Roles
# Roles:
# 1. Tech Lead (6)
# 2. Senior Backend Engineer (10)
# 3. Senior Frontend Engineer (8)
# 4. Fullstack Engineer (10)
# 5. Associate Engineer (6)
EMPLOYEES_RAW = [
    # Tech Leads (6) - Cost $115-130/hr, Capacity 40, Overtime 10
    ("Marcus Brody", "Tech Lead", 125.0, ["System Design", "AWS Cloud"]),
    ("Elena Rostova", "Tech Lead", 130.0, ["System Design", "Machine Learning"]),
    ("Tariq Al-Mansoor", "Tech Lead", 120.0, ["System Design", "Go"]),
    ("Sarah Jenkins", "Tech Lead", 125.0, ["System Design", "Next.js"]),
    ("Kenji Sato", "Tech Lead", 120.0, ["System Design", "PostgreSQL"]),
    ("Amina Diallo", "Tech Lead", 125.0, ["System Design", "AWS Cloud"]),

    # Senior Backend Engineers (10) - Cost $85-100/hr
    ("David Kim", "Senior Backend Engineer", 95.0, ["Go", "Machine Learning"]),
    ("Chloe Dubois", "Senior Backend Engineer", 90.0, ["Python", "FastAPI"]),
    ("Mateo Hernandez", "Senior Backend Engineer", 92.0, ["PostgreSQL", "System Design"]),
    ("Ananya Patel", "Senior Backend Engineer", 95.0, ["Machine Learning", "Python"]),
    ("Liam O'Connor", "Senior Backend Engineer", 88.0, ["Go", "Docker & K8s"]),
    ("Fatima Zahra", "Senior Backend Engineer", 92.0, ["AWS Cloud", "FastAPI"]),
    ("Lucas Silva", "Senior Backend Engineer", 90.0, ["Python", "PostgreSQL"]),
    ("Hanna Lindqvist", "Senior Backend Engineer", 94.0, ["Docker & K8s", "Go"]),
    ("Vikram Malhotra", "Senior Backend Engineer", 96.0, ["Machine Learning", "System Design"]),
    ("Zoe Martin", "Senior Backend Engineer", 88.0, ["FastAPI", "AWS Cloud"]),

    # Senior Frontend Engineers (8) - Cost $80-95/hr
    ("Julian Fischer", "Senior Frontend Engineer", 90.0, ["React Native", "TypeScript"]),
    ("Sofia Morales", "Senior Frontend Engineer", 92.0, ["Next.js", "System Design"]),
    ("Rajesh Iyer", "Senior Frontend Engineer", 88.0, ["React", "TypeScript"]),
    ("Emma Watson", "Senior Frontend Engineer", 85.0, ["Next.js", "React Native"]),
    ("Carlos Mendez", "Senior Frontend Engineer", 90.0, ["TypeScript", "Next.js"]),
    ("Yuki Tanaka", "Senior Frontend Engineer", 92.0, ["React Native", "TypeScript"]),
    ("Nadia Benali", "Senior Frontend Engineer", 88.0, ["Next.js", "React"]),
    ("Benjamin Cohen", "Senior Frontend Engineer", 86.0, ["TypeScript", "React Native"]),

    # Fullstack Engineers (10) - Cost $65-80/hr
    ("Oliver Queen", "Fullstack Engineer", 75.0, ["Next.js", "FastAPI"]),
    ("Grace Hopper", "Fullstack Engineer", 78.0, ["Machine Learning", "Python"]),
    ("Samuel Taylor", "Fullstack Engineer", 70.0, ["React", "PostgreSQL"]),
    ("Leila Farouk", "Fullstack Engineer", 74.0, ["AWS Cloud", "TypeScript"]),
    ("Ethan Hunt", "Fullstack Engineer", 72.0, ["Go", "React"]),
    ("Mia Zhang", "Fullstack Engineer", 76.0, ["Machine Learning", "Next.js"]),
    ("Noah Williams", "Fullstack Engineer", 70.0, ["Docker & K8s", "FastAPI"]),
    ("Clara Oswald", "Fullstack Engineer", 75.0, ["React Native", "PostgreSQL"]),
    ("Diego Alvarez", "Fullstack Engineer", 72.0, ["TypeScript", "AWS Cloud"]),
    ("Kavita Rao", "Fullstack Engineer", 74.0, ["Next.js", "Python"]),

    # Associate Engineers (6) - Cost $45-55/hr
    ("Leo Rossi", "Associate Engineer", 48.0, ["FastAPI", "React"]),
    ("Maya Angel", "Associate Engineer", 50.0, ["TypeScript", "Next.js"]),
    ("Arun Kumar", "Associate Engineer", 45.0, ["Python", "Machine Learning"]),
    ("Sophie Laurent", "Associate Engineer", 52.0, ["React Native", "TypeScript"]),
    ("James Wilson", "Associate Engineer", 48.0, ["PostgreSQL", "Docker & K8s"]),
    ("Zara Khan", "Associate Engineer", 50.0, ["AWS Cloud", "Python"]),
]

# 12 Candidate Projects (3 mandatory, 9 optional)
# Designed for 12-week horizon (weeks 1 to 12)
PROJECTS_DATA = [
    # 1. Mandatory Projects (3)
    {
        "name": "Core Banking Modernization",
        "client": "FinCorp Global",
        "start_week": 1,
        "end_week": 12,
        "revenue": 340000.0,
        "priority": 5,
        "mandatory": True,
        "status": "proposed",
        "roles": [
            {"title": "Lead Architect", "hours": 40, "skills": [("System Design", 4), ("AWS Cloud", 4)], "stretch": False},
            {"title": "Sr Backend Go Dev", "hours": 40, "skills": [("Go", 4), ("PostgreSQL", 4)], "stretch": False},
            {"title": "Sr Backend Python Dev", "hours": 40, "skills": [("Python", 4), ("Docker & K8s", 3)], "stretch": False},
            {"title": "Sr Frontend Next.js Dev", "hours": 40, "skills": [("Next.js", 4), ("TypeScript", 4)], "stretch": False},
        ],
    },
    {
        "name": "Patient Health Portal V2",
        "client": "HealthFirst Network",
        "start_week": 1,
        "end_week": 10,
        "revenue": 250000.0,
        "priority": 5,
        "mandatory": True,
        "status": "proposed",
        "roles": [
            {"title": "Tech Lead", "hours": 40, "skills": [("System Design", 4), ("React", 4)], "stretch": False},
            {"title": "Sr Fullstack Engineer", "hours": 40, "skills": [("FastAPI", 4), ("TypeScript", 3)], "stretch": True},
            {"title": "Security & Cloud Specialist", "hours": 40, "skills": [("AWS Cloud", 4), ("PostgreSQL", 3)], "stretch": False},
        ],
    },
    {
        "name": "Cloud Infrastructure Migration",
        "client": "Global Logistics Corp",
        "start_week": 3,
        "end_week": 10,
        "revenue": 180000.0,
        "priority": 4,
        "mandatory": True,
        "status": "proposed",
        "roles": [
            {"title": "DevOps Architect", "hours": 40, "skills": [("AWS Cloud", 4), ("Docker & K8s", 4)], "stretch": False},
            {"title": "Backend Migration Specialist", "hours": 40, "skills": [("Go", 4), ("PostgreSQL", 4)], "stretch": False},
        ],
    },

    # 2. High-Profit Discretionary Projects
    {
        "name": "Fintech Fraud Detection Engine",
        "client": "SecurePay International",
        "start_week": 1,
        "end_week": 10,
        "revenue": 290000.0,
        "priority": 4,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "ML Lead", "hours": 40, "skills": [("Machine Learning", 4), ("System Design", 4)], "stretch": False},
            {"title": "High-Throughput Backend Dev", "hours": 40, "skills": [("Go", 4), ("PostgreSQL", 4)], "stretch": False},
            {"title": "Data Pipeline Engineer", "hours": 40, "skills": [("Python", 4), ("Docker & K8s", 3)], "stretch": False},
        ],
    },
    {
        "name": "Omnichannel Retail E-Commerce",
        "client": "RetailGiant USA",
        "start_week": 1,
        "end_week": 12,
        "revenue": 280000.0,
        "priority": 4,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "Frontend Lead", "hours": 40, "skills": [("Next.js", 4), ("TypeScript", 4)], "stretch": False},
            {"title": "Fullstack Platform Dev", "hours": 40, "skills": [("React", 3), ("FastAPI", 3)], "stretch": False},
            {"title": "Database Optimization Dev", "hours": 40, "skills": [("PostgreSQL", 4), ("AWS Cloud", 3)], "stretch": False},
        ],
    },
    {
        "name": "Supply Chain IoT Tracking",
        "client": "TrackFast Logistics",
        "start_week": 2,
        "end_week": 11,
        "revenue": 210000.0,
        "priority": 3,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "IoT Backend Architect", "hours": 40, "skills": [("Go", 4), ("Docker & K8s", 4)], "stretch": False},
            {"title": "Real-time Dashboard Dev", "hours": 40, "skills": [("React", 4), ("TypeScript", 3)], "stretch": True},
        ],
    },

    # 3. High-Growth / High-Learning Discretionary Projects (High Stretch Opportunities)
    {
        "name": "AI Customer Support Copilot",
        "client": "TeleComms United",
        "start_week": 1,
        "end_week": 12,
        "revenue": 175000.0,
        "priority": 3,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "AI Mentor & Architect", "hours": 40, "skills": [("Machine Learning", 4), ("Python", 4)], "stretch": False},
            {"title": "Junior AI Applications Dev", "hours": 40, "skills": [("Machine Learning", 3), ("FastAPI", 3)], "stretch": True},
            {"title": "Interactive Chat UI Dev", "hours": 40, "skills": [("Next.js", 3), ("TypeScript", 3)], "stretch": True},
        ],
    },
    {
        "name": "NextGen Mobile Banking App",
        "client": "NeoBank Digital",
        "start_week": 3,
        "end_week": 11,
        "revenue": 185000.0,
        "priority": 4,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "Mobile Lead Mentor", "hours": 40, "skills": [("React Native", 4), ("TypeScript", 4)], "stretch": False},
            {"title": "Stretch Mobile Engineer", "hours": 40, "skills": [("React Native", 3), ("TypeScript", 3)], "stretch": True},
            {"title": "API Integration Dev", "hours": 40, "skills": [("FastAPI", 3), ("PostgreSQL", 3)], "stretch": True},
        ],
    },
    {
        "name": "Autonomous Drone Fleet Ops",
        "client": "AeroVision Systems",
        "start_week": 1,
        "end_week": 10,
        "revenue": 195000.0,
        "priority": 3,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "Computer Vision & ML Lead", "hours": 40, "skills": [("Machine Learning", 4), ("Python", 4)], "stretch": False},
            {"title": "Cloud Infrastructure Engineer", "hours": 40, "skills": [("AWS Cloud", 3), ("Docker & K8s", 3)], "stretch": True},
        ],
    },
    {
        "name": "Data Lakehouse Analytics Platform",
        "client": "InsureTech Capital",
        "start_week": 2,
        "end_week": 12,
        "revenue": 220000.0,
        "priority": 3,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "Lakehouse Architect", "hours": 40, "skills": [("PostgreSQL", 4), ("Python", 4)], "stretch": False},
            {"title": "Cloud Data Engineer", "hours": 40, "skills": [("AWS Cloud", 4), ("Docker & K8s", 3)], "stretch": False},
        ],
    },
    {
        "name": "Enterprise CRM Integration",
        "client": "Apex Advisory",
        "start_week": 4,
        "end_week": 9,
        "revenue": 110000.0,
        "priority": 2,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "Integration Specialist", "hours": 40, "skills": [("Python", 3), ("PostgreSQL", 3)], "stretch": True},
        ],
    },
    {
        "name": "Internal Developer Portal",
        "client": "SaaSWorks Inc",
        "start_week": 2,
        "end_week": 9,
        "revenue": 115000.0,
        "priority": 2,
        "mandatory": False,
        "status": "proposed",
        "roles": [
            {"title": "DevOps Platform Engineer", "hours": 40, "skills": [("Docker & K8s", 4), ("AWS Cloud", 3)], "stretch": False},
            {"title": "UI Dashboard Engineer", "hours": 40, "skills": [("React", 3), ("TypeScript", 3)], "stretch": True},
        ],
    },
]

# Employee Leaves (date ranges within the 12-week horizon)
LEAVES_DATA = [
    # employee_index, start_week, num_weeks, reason
    (1, 4, 3, "Paternity leave"),              # Elena Rostova (Tech Lead) away weeks 4-6
    (7, 6, 2, "Medical procedure & recovery"),  # David Kim (Senior Backend) away weeks 6-7
    (17, 2, 2, "Annual family holiday"),       # Sofia Morales (Senior Frontend) away weeks 2-3
    (25, 8, 3, "Compassionate leave"),         # Samuel Taylor (Fullstack) away weeks 8-10
    (34, 5, 2, "Certification & training"),    # Leo Rossi (Associate) away weeks 5-6
    (38, 9, 2, "Personal leave"),              # James Wilson (Associate) away weeks 9-10
]
