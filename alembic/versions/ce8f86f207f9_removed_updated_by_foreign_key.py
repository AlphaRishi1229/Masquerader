"""Removed updated by foreign key

Revision ID: ce8f86f207f9
Revises: 6b3737d63f88
Create Date: 2020-04-09 17:03:23.727573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce8f86f207f9'
down_revision = '6b3737d63f88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('urls_updated_by_fkey', 'urls', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('urls_updated_by_fkey', 'urls', 'users', ['updated_by'], ['id'])
    # ### end Alembic commands ###
