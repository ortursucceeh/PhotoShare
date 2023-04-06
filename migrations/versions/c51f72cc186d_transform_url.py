"""transform_url

Revision ID: c51f72cc186d
Revises: cab5ce5db318
Create Date: 2023-04-06 14:52:29.044748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c51f72cc186d'
down_revision = 'cab5ce5db318'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('transform_url', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'transform_url')
    # ### end Alembic commands ###