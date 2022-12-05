"""add sources

Revision ID: 0176bc377198
Revises: 470a2e54120c
Create Date: 2022-12-05 13:18:59.532145

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0176bc377198"
down_revision = "470a2e54120c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "source",
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("endpoint", sa.Text(), nullable=True),
        sa.Column("collection", sa.Text(), nullable=True),
        sa.Column("dataset", sa.Text(), nullable=True),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("endpoint_url", sa.Text(), nullable=True),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("organisation", sa.Text(), nullable=True),
        sa.Column("organisation_entity", sa.Text(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("source")
    # ### end Alembic commands ###