from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    active = Column(Boolean, default=True)
    max_load = Column(Integer, default=5)
    source_weights = relationship("OperatorSourceWeight", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    operator_weights = relationship("OperatorSourceWeight", back_populates="source")
    contacts = relationship("Contact", back_populates="source")


class OperatorSourceWeight(Base):
    __tablename__ = "operator_source_weights"
    id = Column(Integer, primary_key=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Float, default=1.0)
    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")
    __table_args__ = (UniqueConstraint("operator_id", "source_id", name="uix_operator_source"),)


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True)
    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
