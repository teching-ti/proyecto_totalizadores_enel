from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura la conexión a la base de datos MySQL
# el modelo de conexion para sqlalchemy es el siguiente: mysql://USUARIO:CONTRASEÑA@SERVIDOR/TABLA
DATABASE_URL = "mysql://ti:jvteching9830@localhost/prueba_totalizadores"
engine = create_engine(DATABASE_URL, echo=False)  # se cambia el valor de echo para elegir si ver los logs o no

# Crea una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase base para los modelos de datos
Base = declarative_base()