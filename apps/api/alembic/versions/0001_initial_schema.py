"""Initial schema migration for Allocate

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-26 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'])
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=True)

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='resource_manager'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_org_id', 'users', ['org_id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 3. Skills
    op.create_table(
        'skills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('org_id', 'name', name='uq_skill_org_name'),
    )
    op.create_index('ix_skills_id', 'skills', ['id'])
    op.create_index('ix_skills_org_id', 'skills', ['org_id'])
    op.create_index('ix_skills_name', 'skills', ['name'])
    op.create_index('ix_skills_category', 'skills', ['category'])

    # 4. Employees
    op.create_table(
        'employees',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('cost_per_hour', sa.Float(), nullable=False, server_default='75.0'),
        sa.Column('weekly_capacity_hours', sa.Integer(), nullable=False, server_default='40'),
        sa.Column('max_overtime_hours', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('career_goals', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('org_id', 'email', name='uq_employee_org_email'),
    )
    op.create_index('ix_employees_id', 'employees', ['id'])
    op.create_index('ix_employees_org_id', 'employees', ['org_id'])
    op.create_index('ix_employees_name', 'employees', ['name'])
    op.create_index('ix_employees_role', 'employees', ['role'])

    # 5. Employee Skills
    op.create_table(
        'employee_skills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', sa.String(length=36), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('proficiency', sa.Integer(), nullable=False),
        sa.Column('growth_target', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('org_id', 'employee_id', 'skill_id', name='uq_emp_skill'),
    )
    op.create_index('ix_employee_skills_id', 'employee_skills', ['id'])
    op.create_index('ix_employee_skills_org_id', 'employee_skills', ['org_id'])
    op.create_index('ix_employee_skills_employee_id', 'employee_skills', ['employee_id'])
    op.create_index('ix_employee_skills_skill_id', 'employee_skills', ['skill_id'])

    # 6. Employee Leaves
    op.create_table(
        'employee_leaves',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_employee_leaves_id', 'employee_leaves', ['id'])
    op.create_index('ix_employee_leaves_org_id', 'employee_leaves', ['org_id'])
    op.create_index('ix_employee_leaves_employee_id', 'employee_leaves', ['employee_id'])

    # 7. Projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('client', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('revenue', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('billing_rate_hourly', sa.Float(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('mandatory', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='proposed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_projects_id', 'projects', ['id'])
    op.create_index('ix_projects_org_id', 'projects', ['org_id'])
    op.create_index('ix_projects_name', 'projects', ['name'])

    # 8. Project Roles
    op.create_table(
        'project_roles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_title', sa.String(length=100), nullable=False),
        sa.Column('hours_per_week', sa.Integer(), nullable=False, server_default='40'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_stretch_allowed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_project_roles_id', 'project_roles', ['id'])
    op.create_index('ix_project_roles_org_id', 'project_roles', ['org_id'])
    op.create_index('ix_project_roles_project_id', 'project_roles', ['project_id'])

    # 9. Project Role Skills
    op.create_table(
        'project_role_skills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_role_id', sa.String(length=36), sa.ForeignKey('project_roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', sa.String(length=36), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('min_proficiency', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('project_role_id', 'skill_id', name='uq_role_skill'),
    )
    op.create_index('ix_project_role_skills_id', 'project_role_skills', ['id'])
    op.create_index('ix_project_role_skills_org_id', 'project_role_skills', ['org_id'])
    op.create_index('ix_project_role_skills_project_role_id', 'project_role_skills', ['project_role_id'])
    op.create_index('ix_project_role_skills_skill_id', 'project_role_skills', ['skill_id'])

    # 10. Plans
    op.create_table(
        'plans',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, server_default='Staffing Plan'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('horizon_weeks', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('profit_weight', sa.Float(), nullable=False, server_default='0.6'),
        sa.Column('growth_weight', sa.Float(), nullable=False, server_default='0.3'),
        sa.Column('balance_weight', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('profit_score', sa.Float(), nullable=True),
        sa.Column('growth_score', sa.Float(), nullable=True),
        sa.Column('balance_penalty', sa.Float(), nullable=True),
        sa.Column('solver_status', sa.String(length=50), nullable=True),
        sa.Column('solver_gap', sa.Float(), nullable=True),
        sa.Column('solver_wall_time_ms', sa.Float(), nullable=True),
        sa.Column('inputs_hash', sa.String(length=64), nullable=True),
        sa.Column('objective_breakdown', sa.JSON(), nullable=True),
        sa.Column('dropped_project_reasons', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_plans_id', 'plans', ['id'])
    op.create_index('ix_plans_org_id', 'plans', ['org_id'])
    op.create_index('ix_plans_status', 'plans', ['status'])

    # 11. Assignments
    op.create_table(
        'assignments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plan_id', sa.String(length=36), sa.ForeignKey('plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_role_id', sa.String(length=36), sa.ForeignKey('project_roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('hours', sa.Integer(), nullable=False),
        sa.Column('is_stretch', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('mentor_id', sa.String(length=36), sa.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('reasons', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_assignments_id', 'assignments', ['id'])
    op.create_index('ix_assignments_org_id', 'assignments', ['org_id'])
    op.create_index('ix_assignments_plan_id', 'assignments', ['plan_id'])
    op.create_index('ix_assignments_employee_id', 'assignments', ['employee_id'])
    op.create_index('ix_assignments_project_role_id', 'assignments', ['project_role_id'])
    op.create_index('ix_assignments_mentor_id', 'assignments', ['mentor_id'])

    # 12. Scenarios
    op.create_table(
        'scenarios',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('base_plan_id', sa.String(length=36), sa.ForeignKey('plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('modified_plan_id', sa.String(length=36), sa.ForeignKey('plans.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('modifications', sa.JSON(), nullable=False),
        sa.Column('diff_summary', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_scenarios_id', 'scenarios', ['id'])
    op.create_index('ix_scenarios_org_id', 'scenarios', ['org_id'])
    op.create_index('ix_scenarios_base_plan_id', 'scenarios', ['base_plan_id'])
    op.create_index('ix_scenarios_modified_plan_id', 'scenarios', ['modified_plan_id'])

    # 13. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('org_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_org_id', 'audit_logs', ['org_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('scenarios')
    op.drop_table('assignments')
    op.drop_table('plans')
    op.drop_table('project_role_skills')
    op.drop_table('project_roles')
    op.drop_table('projects')
    op.drop_table('employee_leaves')
    op.drop_table('employee_skills')
    op.drop_table('employees')
    op.drop_table('skills')
    op.drop_table('users')
    op.drop_table('organizations')
