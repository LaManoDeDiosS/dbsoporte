from functools import wraps
from flask_login import current_user
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # No autenticado

        if current_user.rol != 'admin':
            abort(403)  # Prohibido

        return f(*args, **kwargs)
    return decorated_function


def roles_required(*roles):
    """
    Permite acceso solo a los roles indicados.
    Ejemplo: @roles_required('admin', 'tecnico')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.rol not in roles:
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator