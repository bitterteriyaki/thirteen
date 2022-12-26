"""create levels table

Revision ID: 66f698bbb3a5
Revises:
Create Date: 2022-12-23 19:11:28.997018
"""

from alembic.op import create_table, drop_table
from sqlalchemy import BigInteger, Column

# revision identifiers, used by Alembic.
revision = "66f698bbb3a5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    create_table(
        "levels",
        Column("id", BigInteger, primary_key=True),
        Column("experience", BigInteger, default=0, nullable=False),
    )


def downgrade():
    drop_table("levels")
