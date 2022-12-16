"""add provision reason

Revision ID: 397578893553
Revises: 38fd9e36ff90
Create Date: 2022-12-13 09:15:07.195809

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "397578893553"
down_revision = "38fd9e36ff90"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "provision_reason",
        sa.Column("provision_reason", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("provision_reason"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("provision_reason")
    # ### end Alembic commands ###