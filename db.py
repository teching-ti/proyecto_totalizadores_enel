from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura la conexión a la base de datos MySQL
# el modelo de conexion para sqlalchemy es el siguiente: mysql://USUARIO:CONTRASEÑA@SERVIDOR/BASE

# 1
# en servidor local, se recomienda dejarlo de esta manera para evitar modificaciones de codigo:
DATABASE_URL = "mysql://root:@localhost/prueba_totalizadores"

# Esta cadena de conexion con valores personalizados solo es para prueba, se recomienda usar el de arriba cuando se use en producción en la pc de un usuario
#DATABASE_URL = "mysql://ti:jvteching9830@localhost/prueba_totalizadores"
engine = create_engine(DATABASE_URL, echo=False)  # se cambia el valor de echo para elegir si ver los logs o no

# Crea una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase base para los modelos de datos
Base = declarative_base()

# para los calculos
Session = sessionmaker(bind=engine)
session = Session()

#2
# configuracion para acceder a la base de datos WEB
DATABASE_URL_2 = "mysql://techingc_sa:saSA+-24@170.10.161.194/techingc_DB_Lab"
engine2 = create_engine(DATABASE_URL_2, echo=False)

SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

# Crea una clase base para los modelos de datos
Base2 = declarative_base()

Session2 = sessionmaker(bind=engine2)
session2 = Session2()