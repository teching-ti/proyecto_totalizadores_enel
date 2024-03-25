from db import SessionLocal, session
from sqlalchemy import create_engine, func
from modelos import DatosMedidorConsumo
import datetime

def obtener_suma_kwh_del(fecha_inicio, fecha_fin, meter_id):

    # realizar la consulta y aplicar la función de agregación
    suma_kwh_del = session.query(func.sum(DatosMedidorConsumo.kwh_del)).\
                    filter(DatosMedidorConsumo.meter_id == meter_id).\
                    filter(DatosMedidorConsumo.date >= fecha_inicio).\
                    filter(DatosMedidorConsumo.date <= fecha_fin).scalar()

    return suma_kwh_del

def obtener_consumo_por_dia(fecha_inicio, fecha_fin, meter_id):
    # realizar la consulta y aplicar la función de agregación para sumar el consumo de kwh_del por día
    resultado = session.query(
        DatosMedidorConsumo.date,
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        DatosMedidorConsumo.meter_id == meter_id,
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin
    ).group_by(
        DatosMedidorConsumo.date
    ).all()

    return resultado



fecha_inicio = datetime.datetime(2024, 2, 26).date()
fecha_fin = datetime.datetime(2024, 3, 4).date()

print(obtener_suma_kwh_del(fecha_inicio, fecha_fin, '08119'))