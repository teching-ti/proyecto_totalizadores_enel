from sqlalchemy import Column, Integer, String, Date, Time, Float, DECIMAL
from db import Base

class DatosMedidorConsumo(Base):
    __tablename__ = "datos_medidor_consumo"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)
    kwh_del = Column(DECIMAL(precision=14, scale=8), nullable=True)
    kwh_rec = Column(DECIMAL(precision=14, scale=8), nullable=True)
    kvarh_q1 = Column(DECIMAL(precision=14, scale=8), nullable=True)
    kvarh_q2 = Column(DECIMAL(precision=14, scale=8), nullable=True)
    kvarh_q3 = Column(DECIMAL(precision=14, scale=8), nullable=True)
    kvarh_q4 = Column(DECIMAL(precision=14, scale=8), nullable=True)
    
    # agregar aqui la nueva tabla para el registro de los perfiles de instrumentación