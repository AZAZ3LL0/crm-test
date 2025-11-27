from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Operator, Lead, Source, OperatorSourceWeight, Contact
import random

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini CRM")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/operators/")
def create_operator(name: str, max_load: int = 5, db: Session = Depends(get_db)):
    op = Operator(name=name, max_load=max_load)
    db.add(op)
    db.commit()
    db.refresh(op)
    return {
        "id": op.id, 
        "name": op.name, 
        "max_load": op.max_load, 
        "active": op.active
        }


@app.get("/operators/")
def list_operators(db: Session = Depends(get_db)):
    operators = db.query(Operator).all()
    return [
        {
            "operator_id": o.id,
            "name": o.name,
            "max_load": o.max_load,
            "active": o.active

        } for o in operators
    ]


@app.post("/sources/")
def create_source(name: str, db: Session = Depends(get_db)):
    src = Source(name=name)
    db.add(src)
    db.commit()
    db.refresh(src)
    return {
        "id": src.id, 
        "name": src.name
        }


@app.post("/sources/{source_id}/assign_operator/")
def assign_operator_to_source(source_id: int, operator_id: int, weight: float = 1.0, db: Session = Depends(get_db)):
    src = db.query(Source).filter_by(id=source_id).first()
    op = db.query(Operator).filter_by(id=operator_id).first()
    if not src or not op:
        raise HTTPException(status_code=404, detail="Source or Operator not found")
    link = OperatorSourceWeight(operator=op, source=src, weight=weight)
    db.add(link)
    db.commit()
    db.refresh(link)
    return {
        "operator": op.name, 
        "source": src.name, 
        "weight": link.weight
        }


def choose_operator(source: Source):
    operator_weights = [
        ow for ow in source.operator_weights
        if ow.operator.active and len(ow.operator.contacts) < ow.operator.max_load
    ]
    if not operator_weights:
        return None
    weights = [ow.weight for ow in operator_weights]
    return random.choices([ow.operator for ow in operator_weights], weights=weights, k=1)[0]


@app.post("/contacts/")
def create_contact(lead_id: str, source_name: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter_by(external_id=lead_id).first()
    if not lead:
        lead = Lead(external_id=lead_id)
        db.add(lead)
        db.commit()
        db.refresh(lead)

    source = db.query(Source).filter_by(name=source_name).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    operator = choose_operator(db, source)
    contact = Contact(lead=lead, source=source, operator=operator)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {
        "contact_id": contact.id,
        "lead": lead.external_id,
        "source": source.name,
        "operator": operator.name if operator else None
    }


@app.get("/contacts/")
def list_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return [
        {
            "contact_id": c.id,
            "lead": c.lead.external_id,
            "source": c.source.name,
            "operator": c.operator.name if c.operator else None
        } for c in contacts
    ]



