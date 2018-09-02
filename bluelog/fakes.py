# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.

笔记：
    生成虚拟数据模块
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog import db
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker()
# fake = Faker("zh_CN")

def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, I'm the real thing.",
        name='Mima Kirigoe',
        about='Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            # timestamp=fake.date_time_this_year()      # modify this
            timestamp=fake.past_datetime('-1y')
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        post = Post.query.get(random.randint(1, Post.query.count()))
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            # timestamp=fake.date_time_this_year(),     # modify this
            timestamp=fake.date_time_between_dates(datetime_start=post.timestamp),
            reviewed=True,
            post=post
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # unreviewed comments
        post = Post.query.get(random.randint(1, Post.query.count()))
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            # timestamp=fake.date_time_this_year(),     # modify this
            timestamp=fake.date_time_between_dates(datetime_start=post.timestamp),
            reviewed=False,
            post=post
        )
        db.session.add(comment)

        # from admin
        post = Post.query.get(random.randint(1, Post.query.count()))
        comment = Comment(
            author='Mima Kirigoe',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            # timestamp=fake.date_time_this_year(),     # modify this
            timestamp=fake.date_time_between_dates(datetime_start=post.timestamp),
            from_admin=True,
            reviewed=True,
            post=post
        )
        db.session.add(comment)
    db.session.commit()

    # replies
    for i in range(salt):
        comment = Comment.query.get(random.randint(1, Comment.query.count()))
        reply = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            reviewed=True,
            # timestamp=fake.date_time_this_year(),            
            # replied=Comment.query.get(random.randint(1, Comment.query.count())),
            # post=Post.query.get(random.randint(1, Post.query.count()))

            # 确保回复的时间在评论的时间之后，并且不超过现在的时间
            timestamp=fake.date_time_between_dates(datetime_start=comment.timestamp),
            replied=comment,     # 关联评论
            post=comment.post    # 回复与评论是同一篇文章
        )
        db.session.add(reply)
    db.session.commit()


def fake_links():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()
