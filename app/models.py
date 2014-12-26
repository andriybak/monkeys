from app import db
from hashlib import md5

friends = db.Table("friends",
                   db.Column("friend_id", db.Integer,
                             db.ForeignKey("user.id")),
                   db.Column("friended_id", db.Integer,
                             db.ForeignKey("user.id")))


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120))
    age = db.Column(db.String(2))
    posts = db.relationship("Post", backref="author",
                            lazy="dynamic", cascade="delete")
    bff_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    parent = db.relationship("User", remote_side=[id])
    about_me = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime)
    friend = db.relationship("User", secondary=friends,
                             primaryjoin=(friends.c.friend_id == id),
                             secondaryjoin=(friends.c.friended_id == id),
                             backref=db.backref("friends", lazy="dynamic"),
                             lazy="dynamic", cascade="delete")

    def check_password(self, password):
        if(self.password != password):
            return False
        return True

    def add_bff(self, user):
        if not self.is_bff(user) and self.is_friend(user):
            self.bff_id = user.id
            return self

    def remove_bff(self, user):
        if self.is_bff(user):
            self.bff_id = 0
            return self

    def is_bff(self, user):
        return self.bff_id == user.id

    def get_bff(self):
        return User.query.filter(User.id == self.bff_id).first()

    def friended(self, user):
        if not self.is_friend(user):
            self.friend.append(user)
            return self

    def unfriend(self, user):
        if self.is_friend(user):
            self.friend.remove(user)
            return self

    def is_friend(self, user):
        return self.friend.filter(friends.c.friended_id == user.id).count() > 0

    def friends_posts(self):
        return Post.query.join(friends,
                               (friends.c.friended_id == Post.user_id))\
                .filter(friends.c.friend_id == self.id)\
                .order_by(Post.timestamp.desc())

    def friended_users(self):
        return User.query.join(friends, (friends.c.friended_id == User.id))\
                               .filter(friends.c.friend_id == self.id)\
                               .order_by(User.nickname.asc())

    def users_by_name(self):
        return User.query.order_by(User.nickname.asc())

    def users_by_bff(self):
        return User.query.filter(User.bff is not None).order_by(User.bff.asc())

    def users_by_friends(self):
        return User.query.order_by(asc(self.friend.count()))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def avatar(self, size):
        return "http://www.gravatar.com/avatar/%s?d=retro&s=%d" % \
                (md5(self.email.encode("utf-8")).hexdigest, size)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

