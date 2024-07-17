"""New Table

Revision ID: a95a07959b70
Revises: 
Create Date: 2024-03-31 01:32:42.231921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a95a07959b70'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.String(length=30), nullable=True),
    sa.Column('full_name', sa.String(length=150), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('email_id', sa.String(length=50), nullable=True),
    sa.Column('mobile_number', sa.String(length=20), nullable=True),
    sa.Column('alter_mobile_number', sa.String(length=20), nullable=True),
    sa.Column('address', sa.String(length=455), nullable=True),
    sa.Column('created_by', sa.String(length=30), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_by', sa.String(length=30), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_client_id'), 'client', ['client_id'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('full_name', sa.String(length=200), nullable=True),
    sa.Column('email_id', sa.String(length=50), nullable=True),
    sa.Column('mobile_number', sa.String(length=20), nullable=True),
    sa.Column('password_modified_date', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=30), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_by', sa.String(length=30), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_user_name'), 'user', ['user_name'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_user_name'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_client_client_id'), table_name='client')
    op.drop_table('client')
    # ### end Alembic commands ###
