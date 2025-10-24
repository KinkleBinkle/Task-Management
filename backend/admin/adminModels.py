from sqlalchemy import Column, Integer, String
from database import Base


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)

