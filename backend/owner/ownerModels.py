from sqlalchemy import Column, Integer, String
from database import Base


class Owner(Base):
    __tablename__ = "owner"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)

