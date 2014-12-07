#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta

class TestCase(unittest.TestCase):
 
   def test_follow_posts(self):
        # make 3 monkeys and 1 to test delete
        u1 = User(nickname='alex', email='alex@a.com')
        u2 = User(nickname='david', email='david@a.com')
        u3 = User(nickname='lisa', email='lisa@a.com')

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)

        # make 3 posts
        utcnow = datetime.utcnow()
        p1 = Post(body="alex first post", author=u1, timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="hello from david", author=u2, timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="Hi!!!:)", author=u3, timestamp=utcnow + timedelta(seconds=3))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.commit()

        # friend them
        u1.friend(u2)  # alex - david
        u1.friend(u3)  # alex - lisa
        u2.friend(u3)  # david - lisa        
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()
        # check the followed posts of each user
        db.session.rollback()

if __name__ == '__main__':
    unittest.main()
