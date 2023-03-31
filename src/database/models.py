from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, Text, func
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import aggregated

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now)
    role = Column(String(20), nullable=False)
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
    title = Column(String(50))
    descr = Column(Text)
    created_at = Column(DateTime, default=func.now)
    updated_at = Column(DateTime, default=func.now)
    hashtags = relationship('Hashtag', secondary=post_m2m_hashtag, backref='posts')
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    done = Column(Boolean, default=False) # for update
    
    @aggregated('rating', Column(Numeric))
    def avg_rating(self):
        return func.avg('ratings.rate')

    rating = relationship('Rating', backref="post_id")
    user = relationship('User', backref="posts")
    
    
class Hashtag(Base):
    __tablename__ = 'hashtags'
    id = Column(Integer, primary_key=True)
    title = Column(String(25), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    done = Column(Boolean, default=False) # for update
    
    user = relationship('User', backref="hashtags")
    
    
class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now)
    updated_at = Column(DateTime, default=func.now)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    post_id = Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), default=None)
    done = Column(Boolean, default=False) # for update
     
    user = relationship('User', backref="posts")
    post = relationship('Post', backref="comments")


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    rate = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now)
    updated_at = Column(DateTime, default=func.now)
    post_id = Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    done = Column(Boolean, default=False) # for update
    
    user = relationship('User', backref="ratings")
    post = relationship('Post', backref="rating")

