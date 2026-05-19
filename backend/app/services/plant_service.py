from sqlalchemy.orm import Session

from app.models.plant import Plant
from app.schemas.plant import PlantCreate


def get_plant_by_id(db: Session, plant_id: int) -> Plant | None:
    return db.query(Plant).filter(Plant.id == plant_id).first()


def get_plant_by_scientific_name(db: Session, scientific_name: str) -> Plant | None:
    return db.query(Plant).filter(Plant.scientific_name == scientific_name).first()


def create_plant(db: Session, plant_data: PlantCreate) -> Plant:
    plant = Plant(**plant_data.model_dump())

    db.add(plant)
    db.commit()
    db.refresh(plant)

    return plant