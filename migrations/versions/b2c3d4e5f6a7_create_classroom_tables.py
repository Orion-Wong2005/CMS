"""create classroom tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    """创建 classrooms 和 classroom_schedules 表"""
    op.create_table('classrooms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('classroom_number', sa.String(length=20), nullable=False, comment='教室编号'),
        sa.Column('building', sa.String(length=50), nullable=False, comment='教学楼'),
        sa.Column('floor', sa.Integer(), nullable=True, comment='楼层'),
        sa.Column('capacity', sa.Integer(), nullable=True, comment='容量'),
        sa.Column('type', sa.String(length=20), nullable=True, comment='类型'),
        sa.Column('equipment', sa.String(length=200), nullable=True, comment='设备配置'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('classroom_number')
    )

    op.create_table('classroom_schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False, comment='教室ID'),
        sa.Column('course_id', sa.String(length=20), nullable=False, comment='课程编号'),
        sa.Column('semester', sa.String(length=20), nullable=False, comment='学期'),
        sa.Column('week', sa.Integer(), nullable=False, comment='周次(1-20)'),
        sa.Column('weekday', sa.Integer(), nullable=False, comment='星期几(1-7)'),
        sa.Column('start_section', sa.Integer(), nullable=False, comment='开始节次'),
        sa.Column('end_section', sa.Integer(), nullable=False, comment='结束节次'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('classroom_id', 'semester', 'week', 'weekday', 'start_section',
                            name='uq_classroom_time_slot')
    )


def downgrade():
    """删除 classrooms 和 classroom_schedules 表"""
    op.drop_table('classroom_schedules')
    op.drop_table('classrooms')
