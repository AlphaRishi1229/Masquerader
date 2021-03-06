"""Added latency Column

Revision ID: 8c00d961a9f2
Revises: 7fb5016dff09
Create Date: 2020-02-10 12:26:37.559300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c00d961a9f2'
down_revision = '7fb5016dff09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('urls', sa.Column('latency', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('urls', 'latency')
    # ### end Alembic commands ###
