import jwt
from datetime import datetime, timedelta
from typing import Union


JWT_SECRET = "supersecreto" # Clave secreta para firmar los tokens
JWT_ALGORITHM = "HS256" # Algoritmo de firma de los tokens
JWT_EXP_DELTA_SECONDS = 3600 # Duración del token en segundos

def generate_token(user_id: int) -> str:
    """
    Genera un token JWT válido para el usuario con el id dado.
    """
    # Calculamos el tiempo de expiración del token
    expiration = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)

    # Creamos el payload del token con el id del usuario y la fecha de expiración
    payload = {
        'user_id': user_id,
        'exp': expiration
    }

    # Generamos y devolvemos el token firmado con la clave secreta
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Union[int, None]:
    """
    Verifica si el token dado es válido y devuelve el user_id del usuario si lo es.
    Si el token es inválido o ha expirado, devuelve None.
    """
    try:
        # Decodificamos el token con la clave secreta y el algoritmo de firma
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Obtenemos el user_id del payload y lo devolvemos
        user_id = payload['user_id']
        return user_id

    except jwt.ExpiredSignatureError:
        # El token ha expirado
        return None

    except jwt.InvalidTokenError:
        # El token es inválido
        return None
