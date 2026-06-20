from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./carepage.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_name = Column(
        String,
        nullable=False
    )

    date = Column(
        String,
        nullable=False
    )

    image_path = Column(
        String,
        nullable=False
    )


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()