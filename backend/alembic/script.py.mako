"""
Generic migration script template for Alembic.
This can be left as the default template used when generating revisions.
"""
% from alembic import op
%
revision = "${up_revision}"
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    pass


def downgrade():
    pass
