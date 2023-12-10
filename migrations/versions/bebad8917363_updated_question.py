"""updated_question

Revision ID: bebad8917363
Revises: 247f1ddeec6c
Create Date: 2023-12-10 14:14:34.412762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bebad8917363'
down_revision = '247f1ddeec6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('question', 'material',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=800),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('question', 'material',
               existing_type=sa.String(length=800),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
    # ### end Alembic commands ###