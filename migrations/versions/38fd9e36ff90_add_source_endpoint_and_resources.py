"""add source endpoint and resources

Revision ID: 38fd9e36ff90
Revises: 470a2e54120c
Create Date: 2022-12-08 11:18:56.113494

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "38fd9e36ff90"
down_revision = "470a2e54120c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "resource",
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "resource", "source", "endpoint", "dataset", "organisation"
        ),
    )
    op.create_table(
        "source_endpoint_dataset",
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("endpoint_url", sa.Text(), nullable=False),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("organisation_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("source", "endpoint", "dataset"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("source_endpoint_dataset")
    op.drop_table("resource")
    # ### end Alembic commands ###