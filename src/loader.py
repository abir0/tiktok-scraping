import json

from sqlalchemy import create_engine, Column, Integer, select, String, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker


# Base class for declarative models
Base = declarative_base()


# Video model representing the 'videos' table
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_url = Column(Text, nullable=False)
    video_caption = Column(Text)
    author_username = Column(String, nullable=False)


# User model representing the 'users' table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    following_count = Column(Integer)
    followers_count = Column(Integer)
    likes_count = Column(Integer)


# DatabaseManager class to manage database operations
class DatabaseManager:
    def __init__(self, db_url=None):
        self.engine = create_engine(db_url)
        # Create all tables defined by Base subclasses
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def bulk_insert_video_data(self, video_data):
        """Insert multiple video records into the database."""
        session = self.Session()
        try:
            # Bulk insert video data
            session.bulk_insert_mappings(Video, video_data)
            session.commit()
        except SQLAlchemyError as e:
            # Handle SQL errors, rollback the session
            print(f"Error inserting video data: {e}")
            session.rollback()
        finally:
            session.close()

    def add_user(self, user_data):
        """Add a new user record to the database."""
        session = self.Session()
        try:
            # Create a new User instance and add it to the session
            session.add(User(**user_data))
            session.commit()
        except SQLAlchemyError as e:
            # Handle SQL errors, rollback the session
            print(f"Error adding user: {e}")
            session.rollback()
        finally:
            session.close()

    def get_all_users(self):
        """Retrieve all unique users from the videos table."""
        session = self.Session()
        try:
            # Execute a query to select distinct author usernames
            query = select(Video.author_username).distinct()
            result = session.execute(query).scalars()
            return result.all()
        except SQLAlchemyError as e:
            # Handle SQL errors, rollback the session
            print(f"Error fetching unique authors from videos: {e}")
            session.rollback()
        finally:
            session.close()

    def export_to_json(self, file_name="data.json"):
        session = self.Session()
        try:
            users = session.query(User).all()
            videos = session.query(Video).all()
            data = {
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "following_count": user.following_count,
                        "followers_count": user.followers_count,
                        "likes_count": user.likes_count,
                    }
                    for user in users
                ],
                "videos": [
                    {
                        "id": video.id,
                        "video_url": video.video_url,
                        "video_caption": video.video_caption,
                        "author_username": video.author_username,
                    }
                    for video in videos
                ],
            }
            with open(file_name, "w") as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            print(f"Error exporting data to JSON file:{e}")
        finally:
            session.close()
