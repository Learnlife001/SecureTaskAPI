from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String, nullable=False)  # create, update, delete, restore
    entity_type = Column(String, nullable=False)  # task, user
    entity_id = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")