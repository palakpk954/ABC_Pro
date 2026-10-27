import csv
import io
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.project import Project, ProjectRole
from app.models.skill import Skill
from app.schemas.import_export import CSVImportSummary, CSVRowError
from app.services.audit_service import log_audit


def parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def import_csv_data(
    entity_type: str,
    csv_content: str,
    org_id: str,
    db: Session,
    user_id: Optional[str] = None,
) -> CSVImportSummary:
    """Parses and validates CSV content for employees, skills, projects, or roles."""
    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)

    errors: List[CSVRowError] = []
    imported_ids: List[str] = []
    row_num = 1  # 1-indexed, header is row 1

    if not reader.fieldnames:
        return CSVImportSummary(
            entity_type=entity_type,
            total_rows=0,
            successful_rows=0,
            failed_rows=0,
            errors=[CSVRowError(row_number=1, error_message="Empty CSV or missing header")],
        )

    for row in reader:
        row_num += 1
        # Strip all keys and values
        clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}

        if entity_type == "skills":
            name = clean_row.get("name")
            category = clean_row.get("category", "General")
            desc = clean_row.get("description", "")

            if not name:
                errors.append(CSVRowError(row_number=row_num, field="name", error_message="Skill name is required"))
                continue

            existing = db.query(Skill).filter(Skill.org_id == org_id, Skill.name == name).first()
            if existing:
                existing.category = category
                existing.description = desc
                imported_ids.append(existing.id)
            else:
                new_skill = Skill(org_id=org_id, name=name, category=category, description=desc)
                db.add(new_skill)
                db.flush()
                imported_ids.append(new_skill.id)

        elif entity_type == "employees":
            name = clean_row.get("name")
            email = clean_row.get("email")
            role = clean_row.get("role", "Developer")
            cost_str = clean_row.get("cost_per_hour", "60.0")

            if not name or not email:
                errors.append(CSVRowError(row_number=row_num, field="name/email", error_message="Name and email are required"))
                continue

            try:
                cost = float(cost_str)
            except ValueError:
                errors.append(CSVRowError(row_number=row_num, field="cost_per_hour", value=cost_str, error_message="Invalid float"))
                continue

            cap = int(clean_row.get("weekly_capacity_hours") or 40)
            ot = int(clean_row.get("max_overtime_hours") or 10)
            goals_raw = clean_row.get("career_goals", "")
            career_goals = [g.strip() for g in goals_raw.split(";") if g.strip()]

            existing = db.query(Employee).filter(Employee.org_id == org_id, Employee.email == email).first()
            if existing:
                existing.name = name
                existing.role = role
                existing.cost_per_hour = cost
                existing.weekly_capacity_hours = cap
                existing.max_overtime_hours = ot
                existing.career_goals = career_goals
                imported_ids.append(existing.id)
            else:
                new_emp = Employee(
                    org_id=org_id,
                    name=name,
                    email=email,
                    role=role,
                    cost_per_hour=cost,
                    weekly_capacity_hours=cap,
                    max_overtime_hours=ot,
                    career_goals=career_goals,
                )
                db.add(new_emp)
                db.flush()
                imported_ids.append(new_emp.id)

        elif entity_type == "projects":
            name = clean_row.get("name")
            client = clean_row.get("client")
            st_date_str = clean_row.get("start_date")
            en_date_str = clean_row.get("end_date")
            rev_str = clean_row.get("revenue", "0.0")

            if not name or not client or not st_date_str or not en_date_str:
                errors.append(CSVRowError(row_number=row_num, error_message="Name, client, start_date, and end_date are required"))
                continue

            st_date = parse_date(st_date_str)
            en_date = parse_date(en_date_str)
            if not st_date or not en_date:
                errors.append(CSVRowError(row_number=row_num, error_message="Invalid date format. Expected YYYY-MM-DD"))
                continue

            try:
                rev = float(rev_str)
            except ValueError:
                errors.append(CSVRowError(row_number=row_num, field="revenue", value=rev_str, error_message="Invalid float"))
                continue

            prio = int(clean_row.get("priority") or 3)
            mand = clean_row.get("mandatory", "false").lower() in ["true", "1", "yes"]

            existing = db.query(Project).filter(Project.org_id == org_id, Project.name == name).first()
            if existing:
                existing.client = client
                existing.start_date = st_date
                existing.end_date = en_date
                existing.revenue = rev
                existing.priority = prio
                existing.mandatory = mand
                imported_ids.append(existing.id)
            else:
                new_proj = Project(
                    org_id=org_id,
                    name=name,
                    client=client,
                    start_date=st_date,
                    end_date=en_date,
                    revenue=rev,
                    priority=prio,
                    mandatory=mand,
                    status=clean_row.get("status", "proposed"),
                )
                db.add(new_proj)
                db.flush()
                imported_ids.append(new_proj.id)

        elif entity_type == "roles":
            proj_name_or_id = clean_row.get("project_name_or_id")
            role_title = clean_row.get("role_title")
            st_date_str = clean_row.get("start_date")
            en_date_str = clean_row.get("end_date")

            if not proj_name_or_id or not role_title or not st_date_str or not en_date_str:
                errors.append(CSVRowError(row_number=row_num, error_message="project_name_or_id, role_title, start_date, and end_date are required"))
                continue

            proj = db.query(Project).filter(
                Project.org_id == org_id,
                (Project.id == proj_name_or_id) | (Project.name == proj_name_or_id),
            ).first()
            if not proj:
                errors.append(CSVRowError(row_number=row_num, field="project_name_or_id", error_message=f"Project '{proj_name_or_id}' not found"))
                continue

            st_date = parse_date(st_date_str)
            en_date = parse_date(en_date_str)
            if not st_date or not en_date:
                errors.append(CSVRowError(row_number=row_num, error_message="Invalid date format. Expected YYYY-MM-DD"))
                continue

            hrs = int(clean_row.get("hours_per_week") or 40)
            stretch = clean_row.get("is_stretch_allowed", "false").lower() in ["true", "1", "yes"]

            new_role = ProjectRole(
                org_id=org_id,
                project_id=proj.id,
                role_title=role_title,
                hours_per_week=hrs,
                start_date=st_date,
                end_date=en_date,
                is_stretch_allowed=stretch,
            )
            db.add(new_role)
            db.flush()
            imported_ids.append(new_role.id)

    db.commit()

    log_audit(
        db=db,
        org_id=org_id,
        action=f"import_csv_{entity_type}",
        entity_type=entity_type,
        entity_id="bulk_import",
        user_id=user_id,
        after_state={"imported_count": len(imported_ids), "errors_count": len(errors)},
    )

    total = row_num - 1
    return CSVImportSummary(
        entity_type=entity_type,
        total_rows=total,
        successful_rows=len(imported_ids),
        failed_rows=len(errors),
        errors=errors,
        imported_ids=imported_ids,
    )
