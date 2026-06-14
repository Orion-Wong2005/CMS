"""add schedule fields

Revision ID: a1b2c3d4e5f6
Revises: d4ee514fe6e4
Create Date: 2026-06-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd4ee514fe6e4'
branch_labels = None
depends_on = None


def upgrade():
    """为 schedules 表新增 semester、week_start、week_end 字段"""
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('semester', sa.String(length=30), nullable=True, comment='学期'))
        batch_op.add_column(sa.Column('week_start', sa.Integer(), nullable=True, comment='起始周次'))
        batch_op.add_column(sa.Column('week_end', sa.Integer(), nullable=True, comment='结束周次'))


def downgrade():
    """回退：删除新增字段"""
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_column('week_end')
        batch_op.drop_column('week_start')
        batch_op.drop_column('semester')
