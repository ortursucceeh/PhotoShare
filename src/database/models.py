import enum

from sqlalchemy import Boolean, Column, DateTime,ForeignKey, Integer, Numeric, String, Table, Text, func
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
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE")),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id", ondelete="CASCADE")),
)


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    image_url = Column(String(300))
    transform_url = Column(Text)
    title = Column(String(50), nullable=True)
    descr = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    hashtags = relationship('Hashtag', secondary=post_m2m_hashtag, backref='posts')
    done = Column(Boolean, default=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    public_id = Column(String(50))

    @aggregated('rating', Column(Numeric))
    def avg_rating(self):
           return func.avg(Rating.rate)
    
    rating = relationship('Rating')
    user = relationship('User', backref="posts")


class Hashtag(Base):
    __tablename__ = 'hashtags'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(25), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    
    user = relationship('User', backref="hashtags")


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=None)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    post_id = Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), default=None)
    update_status = Column(Boolean, default=False)

    user = relationship('User', backref="comments")
    post = relationship('Post', backref="comments")


class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    rate = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    post_id = Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)

    user = relationship('User', backref="ratings")


# Create Black list of access token
class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False)
    blacklisted_on = Column(DateTime, default=func.now())
