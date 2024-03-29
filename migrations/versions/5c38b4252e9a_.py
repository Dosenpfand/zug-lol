"""empty message

Revision ID: 5c38b4252e9a
Revises: 4dc24a017e3e
Create Date: 2022-11-02 20:18:52.593092

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c38b4252e9a"
down_revision = "4dc24a017e3e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("journey", "date", existing_type=sa.DATE(), nullable=False)
    # op.add_column('user', sa.Column('klimaticket_start_date', sa.Date(), nullable=False))
    # ### end Alembic commands ###
    op.add_column("user", sa.Column("klimaticket_start_date", sa.Date(), nullable=True))

    op.execute("UPDATE \"user\" SET klimaticket_start_date = '2021-11-02'")

    op.alter_column("user", "klimaticket_start_date", nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "klimaticket_start_date")
    op.alter_column("journey", "date", existing_type=sa.DATE(), nullable=True)
    # ### end Alembic commands ###
