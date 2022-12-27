"""create currency table

Revision ID: 2e2e17b4cdd2
Revises: 66f698bbb3a5
Create Date: 2022-12-26 23:14:01.120365
"""

from alembic.op import create_table, drop_table
from sqlalchemy import BigInteger, Column

# revision identifiers, used by Alembic.
revision = "2e2e17b4cdd2"
down_revision = "66f698bbb3a5"
branch_labels = None
depends_on = None


def upgrade():
    create_table(
        "currency",
        Column("id", BigInteger, primary_key=True),
        Column("balance", BigInteger, default=0, nullable=False),
    )


def downgrade():
    drop_table("currency")
