from sqlmodel import Session, create_engine

import app.crud as crud
from app.core.config import settings
from app.models import User

print("TABLA DE USER:", User.__tablename__)
print("CAMPOS DE USER:", list(User.model_fields.keys()))

motor = create_engine(str(settings.DATABASE_URL))
with Session(motor) as sesion:
    try:
        usuario = crud.get_user_by_email(
            session=sesion, email="admin@proteccioncivil.gob.mx"
        )
        print("USUARIO OBTENIDO POR CRUD:", usuario)
    except Exception as e:
        print("ERROR EN CRUD GET USER:", type(e), e)
