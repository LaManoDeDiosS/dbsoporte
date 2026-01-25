print(">>> INICIANDO SCRIPT <<<")

from app import app
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    print(">>> CONTEXTO DE APP CARGADO <<<")

    usuario = Usuario.query.filter_by(email='tecnico@dbsoporte.com').first()

    if not usuario:
        print("❌ USUARIO NO ENCONTRADO")
    else:
        print(f">>> USUARIO ENCONTRADO: {usuario.email}")

        usuario.password = generate_password_hash('admin123')
        db.session.commit()

        print("✅ PASSWORD ACTUALIZADO CORRECTAMENTE")
