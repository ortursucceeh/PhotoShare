import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, Text, func
# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import aggregated
from sqlalchemy import Enum

Base = declarative_base()


class UserRoleEnum(enum.Enum):
    user = 'User'
    moder = 'Moderator'
    admin = 'Administrator'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(355), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    role = Column('role', Enum(UserRoleEnum), default=UserRoleEnum.user)
    refresh_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verify = Column(Boolean, default=False)


post_m2m_hashtag = Table(
    "post_m2m_hashtag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(200))
    transform_url = Column(String(200))
    title = Column(String(50))
    descr = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    done = Column(Boolean, default=False)  # for update
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    hashtags = relationship('Hashtag', secondary=post_m2m_hashtag, backref='posts')

    # @aggregated('rating', Column(Numeric))
    # def avg_rating(self):
    #     """
    #     The avg_rating function returns the average rating for a given movie.
    #     It is used in conjunction with the Movie model to return an average rating
    #     for each movie.

    #     :param self: Refer to the object itself
    #     :return: The average rating for a movie
    #     :doc-author: Trelent
    #     """
    #     return func.avg('ratings.rate')

    # rating = relationship('Rating', backref="post_id")
    user = relationship('User', backref="posts")


class Hashtag(Base):
    __tablename__ = 'hashtags'
    id = Column(Integer, primary_key=True)
    title = Column(String(25), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="hashtags")


# class Comment(Base):
#     __tablename__ = 'comments'
#     id = Column(Integer, primary_key=True)
#     text = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=func.now)
#     updated_at = Column(DateTime, default=func.now)
#     user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
#     post_id = Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), default=None)
#     done = Column(Boolean, default=False)  # for update

#     user = relationship('User', backref="comments")
#     post = relationship('Post', backref="comments")


# class Rating(Base):
#     __tablename__ = 'ratings'
#     id = Column(Integer, primary_key=True)
#     rate = Column(Integer, nullable=False)
#     created_at = Column(DateTime, default=func.now)
#     updated_at = Column(DateTime, default=func.now)
#     user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
#     done = Column(Boolean, default=False)  # for update

#     user = relationship('User', backref="ratings")

