"""new fiedls added

Revision ID: 6584fc53474a
Revises: a95a07959b70
Create Date: 2024-04-11 04:31:57.605819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6584fc53474a'
down_revision = 'a95a07959b70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('adhaar_number', sa.String(length=12), nullable=True))
    op.add_column('client', sa.Column('gender', sa.String(length=8), nullable=True))
    op.add_column('client', sa.Column('dob', sa.Date(), nullable=True))
    op.add_column('client', sa.Column('martial_status', sa.String(length=10), nullable=True))
    op.add_column('client', sa.Column('marriage_date', sa.Date(), nullable=True))
    op.add_column('client', sa.Column('spouse_name', sa.String(length=60), nullable=True))
    op.add_column('client', sa.Column('spouse_mobile_number', sa.String(length=20), nullable=True))
    op.add_column('client', sa.Column('spouse_adhaar_number', sa.String(length=12), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('client', 'spouse_adhaar_number')
    op.drop_column('client', 'spouse_mobile_number')
    op.drop_column('client', 'spouse_name')
    op.drop_column('client', 'marriage_date')
    op.drop_column('client', 'martial_status')
    op.drop_column('client', 'dob')
    op.drop_column('client', 'gender')
    op.drop_column('client', 'adhaar_number')
    # ### end Alembic commands ###