from extensions import db
from flask_login import UserMixin
from datetime import datetime


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(20), default='lector')
    ordenes_creadas = db.relationship('Orden',foreign_keys='Orden.usuario_id',back_populates='usuario_creador')
    ordenes_editadas = db.relationship('Orden',foreign_keys='Orden.usuario_edita_id',back_populates='usuario_editor')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    ordenes = db.relationship('Orden', back_populates='cliente')

class Orden(db.Model):
    __tablename__ = 'ordenes'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False, unique=True)
    persona_reporta = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_edita_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    usuario_creador = db.relationship('Usuario',foreign_keys=[usuario_id],back_populates='ordenes_creadas')
    usuario_editor = db.relationship('Usuario',foreign_keys=[usuario_edita_id],back_populates='ordenes_editadas')
    cliente = db.relationship('Cliente', back_populates='ordenes')
    adjuntos = db.relationship('Adjunto',back_populates='orden',cascade='all, delete-orphan')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime)



class Adjunto(db.Model):
    __tablename__ = 'adjuntos'
    id = db.Column(db.Integer, primary_key=True)
    archivo = db.Column(db.String(255), nullable=False)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=False)
    orden = db.relationship('Orden', back_populates='adjuntos')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario')
