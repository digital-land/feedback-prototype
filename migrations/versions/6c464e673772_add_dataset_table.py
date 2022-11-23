"""Add dataset table

Revision ID: 6c464e673772
Revises: 533a24fa186f
Create Date: 2022-11-22 13:19:41.955289

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6c464e673772"
down_revision = "533a24fa186f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "dataset",
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("dataset"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("dataset")
    # ### end Alembic commands ###
