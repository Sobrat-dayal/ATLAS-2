"""stage14_authorization

Revision ID: stage14_authorization
Revises: 08480975c632
Create Date: 2026-10-04 12:13:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'stage14_authorization'
down_revision: Union[str, Sequence[str], None] = '08480975c632'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Tables
    authz_roles = op.create_table('authz_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    authz_permissions = op.create_table('authz_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('risk_class', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_check_constraint(
        'check_risk_class_valid',
        'authz_permissions',
        "risk_class IN ('read', 'write', 'action', 'critical')"
    )

    authz_role_permissions = op.create_table('authz_role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['permission_id'], ['authz_permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['authz_roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    authz_user_roles = op.create_table('authz_user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('assigned_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['authz_roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_index(op.f('ix_authz_user_roles_role_id'), 'authz_user_roles', ['role_id'], unique=False)
    op.create_index(op.f('ix_authz_user_roles_user_id'), 'authz_user_roles', ['user_id'], unique=False)

    # 2. Seed Permissions
    permissions = [
        ("atlas.access", "Atlas Access", "Base access to the ATLAS application.", "read"),
        ("module.home.view", "View Home", "View the Home module.", "read"),
        ("module.markets.view", "View Markets", "View the Markets module.", "read"),
        ("module.charts.view", "View Charts", "View the Charts module.", "read"),
        ("module.watchlists.view", "View Watchlists", "View the Watchlists module.", "read"),
        ("module.screeners.view", "View Screeners", "View the Screeners module.", "read"),
        ("module.companies.view", "View Companies", "View the Companies module.", "read"),
        ("module.economics.view", "View Economics", "View the Economics module.", "read"),
        ("module.news.view", "View News", "View the News module.", "read"),
        ("module.research.view", "View Research", "View the Research module.", "read"),
        ("module.maps.view", "View Maps", "View the Maps module.", "read"),
        ("module.intelligence.view", "View Intelligence", "View the Intelligence module.", "read"),
        ("module.options.view", "View Options", "View the Options module.", "read"),
        ("module.trading.view", "View Trading", "View the Trading module.", "read"),
        ("module.portfolios.view", "View Portfolios", "View the Portfolios module.", "read"),
        ("module.risk.view", "View Risk", "View the Risk module.", "read"),
        ("module.ai.view", "View AI", "View the AI module.", "read"),
        ("module.data.view", "View Data", "View the Data module.", "read"),
        ("module.saved.view", "View Saved", "View the Saved module.", "read"),
        ("module.workspaces.view", "View Workspaces", "View the Workspaces module.", "read"),
        ("module.agents.view", "View Agents", "View the Agents module.", "read"),
        ("settings.read", "Read Settings", "View application settings.", "read"),
        ("settings.write_self", "Write Settings (Self)", "Modify own settings.", "write"),
        ("authz.read", "Read Authorization", "View roles and permissions.", "read"),
        ("authz.manage", "Manage Authorization", "Manage user roles and authorization settings.", "critical"),
    ]
    
    perm_map = {}
    for code, name, desc, risk in permissions:
        perm_id = uuid.uuid4()
        perm_map[code] = perm_id
        op.execute(
            authz_permissions.insert().values(
                id=perm_id,
                code=code,
                name=name,
                description=desc,
                risk_class=risk,
            )
        )

    # 3. Seed Roles
    member_id = uuid.uuid4()
    op.execute(
        authz_roles.insert().values(
            id=member_id,
            key="member",
            name="Member",
            description="Default member access",
            is_system=True
        )
    )

    admin_id = uuid.uuid4()
    op.execute(
        authz_roles.insert().values(
            id=admin_id,
            key="admin",
            name="Administrator",
            description="System administrator",
            is_system=True
        )
    )

    # 4. Map Permissions to Roles
    member_permissions = [
        "atlas.access",
        "module.home.view",
        "module.markets.view",
        "module.charts.view",
        "module.watchlists.view",
        "module.screeners.view",
        "module.companies.view",
        "module.economics.view",
        "module.news.view",
        "module.research.view",
        "module.maps.view",
        "module.intelligence.view",
        "module.options.view",
        "module.trading.view",
        "module.portfolios.view",
        "module.risk.view",
        "module.ai.view",
        "module.data.view",
        "module.saved.view",
        "module.workspaces.view",
        "module.agents.view",
        "settings.read",
        "settings.write_self"
    ]
    
    for perm_code in member_permissions:
        op.execute(
            authz_role_permissions.insert().values(
                role_id=member_id,
                permission_id=perm_map[perm_code]
            )
        )
        # Admin gets everything member gets, plus admin permissions
        op.execute(
            authz_role_permissions.insert().values(
                role_id=admin_id,
                permission_id=perm_map[perm_code]
            )
        )
        
    admin_only_permissions = [
        "authz.read",
        "authz.manage"
    ]
    for perm_code in admin_only_permissions:
        op.execute(
            authz_role_permissions.insert().values(
                role_id=admin_id,
                permission_id=perm_map[perm_code]
            )
        )


def downgrade() -> None:
    op.drop_index(op.f('ix_authz_user_roles_user_id'), table_name='authz_user_roles')
    op.drop_index(op.f('ix_authz_user_roles_role_id'), table_name='authz_user_roles')
    op.drop_table('authz_user_roles')
    op.drop_table('authz_role_permissions')
    op.drop_table('authz_permissions')
    op.drop_table('authz_roles')
