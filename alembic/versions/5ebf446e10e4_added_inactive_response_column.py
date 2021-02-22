"""Added inactive response column

Revision ID: 5ebf446e10e4
Revises: 38ce347f06b0
Create Date: 2020-03-04 18:23:40.671090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ebf446e10e4'
down_revision = '38ce347f06b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('urls', sa.Column('inactive_response', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('urls', 'inactive_response')
    # ### end Alembic commands ###