"""empty message

Revision ID: 8f1f7de63334
Revises: 5c38b4252e9a
Create Date: 2022-11-02 22:46:46.827432

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f1f7de63334"
down_revision = "5c38b4252e9a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user", "klimaticket_start_date", existing_type=sa.DATE(), nullable=True
    )
    op.execute('UPDATE "user" SET klimaticket_start_date = NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user", "klimaticket_start_date", existing_type=sa.DATE(), nullable=False
    )
    # ### end Alembic commands ###
