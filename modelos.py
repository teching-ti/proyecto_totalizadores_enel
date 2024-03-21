from sqlalchemy import Column, Integer, String, Date, Time, Float
from db import Base

class DatosMedidorConsumo(Base):
    __tablename__ = "datos_medidor_consumo"

    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)
    kwh_del = Column(Float, nullable=True)
    kwh_rec = Column(Float, nullable=True)
    kvarh_q1 = Column(Float, nullable=True)
    kvarh_q2 = Column(Float, nullable=True)
    kvarh_q3 = Column(Float, nullable=True)
    kvarh_q4 = Column(Float, nullable=True)