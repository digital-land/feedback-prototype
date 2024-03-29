"""add entity numbers to resource

Revision ID: 97d08be7d53e
Revises: 3ae1cc4edeb7
Create Date: 2022-12-14 14:03:23.673796

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "97d08be7d53e"
down_revision = "3ae1cc4edeb7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("resource", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "entity_numbers", postgresql.ARRAY(sa.BigInteger()), nullable=True
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("resource", schema=None) as batch_op:
        batch_op.drop_column("entity_numbers")

    # ### end Alembic commands ###
