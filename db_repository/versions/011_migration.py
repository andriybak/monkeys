from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
bff = Table('bff', pre_meta,
    Column('friend_id', INTEGER),
    Column('bff_id', INTEGER),
)

bffs = Table('bffs', post_meta,
    Column('friend_id', Integer),
    Column('bff_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['bff'].drop()
    post_meta.tables['bffs'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['bff'].create()
    post_meta.tables['bffs'].drop()
