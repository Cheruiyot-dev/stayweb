"""update table columns

Revision ID: 45278203e025
Revises: 773d4266a530
Create Date: 2024-09-17 03:02:08.702520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45278203e025'
down_revision = '773d4266a530'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('table_reservations', schema=None) as batch_op:
        batch_op.drop_constraint('table_reservations_guest_id_fkey', type_='foreignkey')
        batch_op.drop_column('guest_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('table_reservations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('guest_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('table_reservations_guest_id_fkey', 'guests', ['guest_id'], ['id'])

    # ### end Alembic commands ###
