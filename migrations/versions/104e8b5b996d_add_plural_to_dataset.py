"""add plural to dataset

Revision ID: 104e8b5b996d
Revises: 97d08be7d53e
Create Date: 2023-01-04 11:16:22.293791

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "104e8b5b996d"
down_revision = "97d08be7d53e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(sa.Column("plural", sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_column("plural")

    # ### end Alembic commands ###
