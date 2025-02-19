"""Initial migration

Revision ID: 6bd07eb605e3
Revises: 1c37d72512ff
Create Date: 2025-02-19 17:33:32.994974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bd07eb605e3'
down_revision: Union[str, None] = '1c37d72512ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email_verified', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('phone_verified', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'phone_verified')
    op.drop_column('users', 'email_verified')
    # ### end Alembic commands ###
