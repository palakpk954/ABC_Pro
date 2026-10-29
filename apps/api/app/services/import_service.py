"""CSV Ingestion & Row-Level Validation Service

Parses and validates CSV data for Skills, Employees, Projects, and Roles,
returning detailed row-level validation errors.
"""

import io
import csv
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import (
    Skill,
    Employee,
    Project,
    ProjectRole,
)
from app.schemas.import_csv import CSVImportResult, RowValidationError


def parse_date(date_str: str) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def import_skills_csv(db: Session, org_id: str, content: str) -> CSVImportResult:
    reader = csv.DictReader(io.StringIO(content))
    errors: List[RowValidationError] = []
    imported = 0
    total = 0

    if not reader.fieldnames or "name" not in reader.fieldnames or "category" not in reader.fieldnames:
        return CSVImportResult(
            entity_type="skills",
            total_rows=0,
            imported_rows=0,
            failed_rows=0,
            errors=[RowValidationError(row_number=1, field="header", error_message="CSV must include 'name' and 'category' columns")],
            message="Invalid CSV header",
        )

    for idx, row in enumerate(reader, start=2):
        total += 1
        name = row.get("name", "").strip()
        category = row.get("category", "").strip()
        desc = row.get("description", "").strip() or None

        if not name:
            errors.append(RowValidationError(row_number=idx, field="name", error_message="Skill name cannot be empty"))
            continue
        if not category:
            errors.append(RowValidationError(row_number=idx, field="category", error_message="Skill category cannot be empty"))
            continue

        existing = db.query(Skill).filter(Skill.org_id == org_id, Skill.name == name).first()
        if not existing:
            new_skill = Skill(org_id=org_id, name=name, category=category, description=desc)
            db.add(new_skill)
            imported += 1
        else:
            existing.category = category
            if desc:
                existing.description = desc
            imported += 1

    db.commit()
    return CSVImportResult(
        entity_type="skills",
        total_rows=total,
        imported_rows=imported,
        failed_rows=len(errors),
        errors=errors,
        message=f"Successfully imported {imported} of {total} skills",
    )


def import_employees_csv(db: Session, org_id: str, content: str) -> CSVImportResult:
    reader = csv.DictReader(io.StringIO(content))
    errors: List[RowValidationError] = []
    imported = 0
    total = 0

    required_fields = ["name", "email", "role", "cost_per_hour", "start_date"]
    if not reader.fieldnames or any(rf not in reader.fieldnames for rf in required_fields):
        return CSVImportResult(
            entity_type="employees",
            total_rows=0,
            imported_rows=0,
            failed_rows=0,
            errors=[RowValidationError(row_number=1, field="header", error_message=f"CSV must include columns: {', '.join(required_fields)}")],
            message="Invalid CSV header",
        )

    for idx, row in enumerate(reader, start=2):
        total += 1
        name = row.get("name", "").strip()
        email = row.get("email", "").strip()
        role = row.get("role", "").strip()
        cost_str = row.get("cost_per_hour", "").strip()
        start_str = row.get("start_date", "").strip()

        if not name:
            errors.append(RowValidationError(row_number=idx, field="name", error_message="Name is required"))
            continue
        if "@" not in email or "." not in email:
            errors.append(RowValidationError(row_number=idx, field="email", value=email, error_message="Invalid email address"))
            continue
        if not role:
            errors.append(RowValidationError(row_number=idx, field="role", error_message="Role is required"))
            continue

        try:
            cost = float(cost_str)
            if cost <= 0:
                raise ValueError()
        except ValueError:
            errors.append(RowValidationError(row_number=idx, field="cost_per_hour", value=cost_str, error_message="Cost per hour must be a positive number"))
            continue

        start_d = parse_date(start_str)
        if not start_d:
            errors.append(RowValidationError(row_number=idx, field="start_date", value=start_str, error_message="Invalid date format (use YYYY-MM-DD)"))
            continue

        cap = int(row.get("weekly_capacity_hours", 40) or 40)
        ot = int(row.get("max_overtime_hours", 10) or 10)

        existing = db.query(Employee).filter(Employee.org_id == org_id, Employee.email == email).first()
        if not existing:
            emp = Employee(
                org_id=org_id,
                name=name,
                email=email,
                role=role,
                cost_per_hour=cost,
                weekly_capacity_hours=cap,
                max_overtime_hours=ot,
                start_date=start_d,
                career_goals=[],
            )
            db.add(emp)
        else:
            existing.name = name
            existing.role = role
            existing.cost_per_hour = cost
            existing.weekly_capacity_hours = cap
            existing.max_overtime_hours = ot

        imported += 1

    db.commit()
    return CSVImportResult(
        entity_type="employees",
        total_rows=total,
        imported_rows=imported,
        failed_rows=len(errors),
        errors=errors,
        message=f"Successfully imported {imported} of {total} employees",
    )


def import_projects_csv(db: Session, org_id: str, content: str) -> CSVImportResult:
    reader = csv.DictReader(io.StringIO(content))
    errors: List[RowValidationError] = []
    imported = 0
    total = 0

    required_fields = ["name", "client", "start_date", "end_date", "revenue"]
    if not reader.fieldnames or any(rf not in reader.fieldnames for rf in required_fields):
        return CSVImportResult(
            entity_type="projects",
            total_rows=0,
            imported_rows=0,
            failed_rows=0,
            errors=[RowValidationError(row_number=1, field="header", error_message=f"CSV must include columns: {', '.join(required_fields)}")],
            message="Invalid CSV header",
        )

    for idx, row in enumerate(reader, start=2):
        total += 1
        name = row.get("name", "").strip()
        client = row.get("client", "").strip()
        start_str = row.get("start_date", "").strip()
        end_str = row.get("end_date", "").strip()
        rev_str = row.get("revenue", "").strip()
        priority_str = row.get("priority", "3").strip()
        mand_str = row.get("mandatory", "false").strip().lower()

        if not name or not client:
            errors.append(RowValidationError(row_number=idx, field="name/client", error_message="Project name and client are required"))
            continue

        start_d = parse_date(start_str)
        end_d = parse_date(end_str)
        if not start_d or not end_d:
            errors.append(RowValidationError(row_number=idx, field="dates", error_message="Invalid start or end date format"))
            continue
        if start_d > end_d:
            errors.append(RowValidationError(row_number=idx, field="dates", error_message="Project start date cannot be after end date"))
            continue

        try:
            revenue = float(rev_str)
            if revenue < 0:
                raise ValueError()
        except ValueError:
            errors.append(RowValidationError(row_number=idx, field="revenue", value=rev_str, error_message="Revenue must be a non-negative number"))
            continue

        try:
            priority = int(priority_str)
            if priority < 1 or priority > 5:
                raise ValueError()
        except ValueError:
            errors.append(RowValidationError(row_number=idx, field="priority", value=priority_str, error_message="Priority must be between 1 and 5"))
            continue

        mandatory = mand_str in ("true", "1", "yes", "t")

        existing = db.query(Project).filter(Project.org_id == org_id, Project.name == name).first()
        if not existing:
            proj = Project(
                org_id=org_id,
                name=name,
                client=client,
                start_date=start_d,
                end_date=end_d,
                revenue=revenue,
                priority=priority,
                mandatory=mandatory,
            )
            db.add(proj)
        else:
            existing.client = client
            existing.start_date = start_d
            existing.end_date = end_d
            existing.revenue = revenue
            existing.priority = priority
            existing.mandatory = mandatory

        imported += 1

    db.commit()
    return CSVImportResult(
        entity_type="projects",
        total_rows=total,
        imported_rows=imported,
        failed_rows=len(errors),
        errors=errors,
        message=f"Successfully imported {imported} of {total} projects",
    )
