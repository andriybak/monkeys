from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
friends = Table('friends', pre_meta,
    Column('follower_id', INTEGER),
    Column('followed_id', INTEGER),
)

friends = Table('friends', post_meta,
    Column('friend_id', Integer),
    Column('friended_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['friends'].columns['followed_id'].drop()
    pre_meta.tables['friends'].columns['follower_id'].drop()
    post_meta.tables['friends'].columns['friend_id'].create()
    post_meta.tables['friends'].columns['friended_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['friends'].columns['followed_id'].create()
    pre_meta.tables['friends'].columns['follower_id'].create()
    post_meta.tables['friends'].columns['friend_id'].drop()
    post_meta.tables['friends'].columns['friended_id'].drop()
