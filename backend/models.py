import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Integer,
    DateTime, Date, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


def _uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    tin = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    documents = relationship("Document", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    tax_computations = relationship("TaxComputation", back_populates="user")
    tax_reports = relationship("TaxReport", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"))
    file_name = Column(String(255))
    file_type = Column(String(20))
    upload_path = Column(Text)
    status = Column(String(50), default="uploaded")
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
    transactions = relationship("Transaction", back_populates="document")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.document_id"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"))
    date = Column(Date)
    description = Column(Text)
    amount = Column(Numeric(15, 2))
    direction = Column(String(10))
    category = Column(String(50))
    sub_category = Column(String(100))
    classification_method = Column(String(20))
    confidence_score = Column(Numeric(5, 4))
    user_corrected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    document = relationship("Document", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


class TaxComputation(Base):
    __tablename__ = "tax_computations"

    computation_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"))
    tax_year = Column(Integer)
    gross_income = Column(Numeric(15, 2))
    cra_fixed = Column(Numeric(15, 2))
    cra_percentage = Column(Numeric(15, 2))
    total_cra = Column(Numeric(15, 2))
    pension_relief = Column(Numeric(15, 2))
    nhf_relief = Column(Numeric(15, 2))
    nhis_relief = Column(Numeric(15, 2))
    other_deductions = Column(Numeric(15, 2))
    taxable_income = Column(Numeric(15, 2))
    tax_liability = Column(Numeric(15, 2))
    effective_rate = Column(Numeric(6, 4))
    band_breakdown = Column(JSONB)
    computed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="tax_computations")
    tax_reports = relationship("TaxReport", back_populates="computation")


class TaxReport(Base):
    __tablename__ = "tax_reports"

    report_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"))
    computation_id = Column(UUID(as_uuid=False), ForeignKey("tax_computations.computation_id"))
    report_path = Column(Text)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="tax_reports")
    computation = relationship("TaxComputation", back_populates="tax_reports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(UUID(as_uuid=False))
    action = Column(String(100))
    details = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)


class StatutoryParameter(Base):
    __tablename__ = "statutory_parameters"

    param_id = Column(Integer, primary_key=True, autoincrement=True)
    param_key = Column(String(100), unique=True, nullable=False)
    param_value = Column(Numeric(15, 4))
    description = Column(Text)
    effective_year = Column(Integer, default=2024)
