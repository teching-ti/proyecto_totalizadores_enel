from sqlalchemy import Column, Integer, String, Date, Time, DECIMAL
from db import Base, Base2

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

class DatosMedidorInstrumentacion(Base):
    # agregar aqui la nueva tabla para el registro de los perfiles de instrumentación
    __tablename__ = "datos_medidor_instrumentacion"
    
    # determinar que campos serán registrados en la base de datos
    # comparar los diferentes formatos para perfiles de instrumentación
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)
    int_len = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_a_voltage = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_b_voltage = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_c_voltage = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_a_current = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_b_current = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_c_current = Column(DECIMAL(precision=14, scale=8), nullable=True)
    end_phase_a_pf = Column(DECIMAL(precision=14, scale=8), nullable=True)
    end_phase_b_pf = Column(DECIMAL(precision=14, scale=8), nullable=True)
    end_phase_c_pf = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_line_frequency = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_a_kw = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_b_kw = Column(DECIMAL(precision=14, scale=8), nullable=True)
    average_phase_c_kw = Column(DECIMAL(precision=14, scale=8), nullable=True)

class Medidores(Base):
    # agregar aqui la nueva tabla para el registro de los medidores
    __tablename__ = "medidores"
    
    id = Column(String, primary_key=True)
    sed = Column(String, nullable=True)
    fecha_instalacion = Column(Date, nullable=True)
    marca = Column(String, nullable=True)
    factor = Column(DECIMAL(precision=6, scale=2), nullable=True)

class Permitidos(Base2):
    __tablename__ = 'permitidos'

    usuario = Column(String, primary_key=True)
    serie = Column(String, nullable=False)