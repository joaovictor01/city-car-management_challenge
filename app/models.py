import enum

from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class VehicleColorEnum(enum.Enum):
    yellow = "yellow"
    blue = "blue"
    gray = "gray"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class VehicleModelEnum(enum.Enum):
    hatch = "hatch"
    sedan = "sedan"
    convertible = "convertible"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Person(db.Model):
    __tablename__ = "persons"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sale_oportunity = db.Column(db.Boolean, default=False)
    vehicles = db.relationship(
        "Vehicle",
        backref="person",
        lazy="dynamic",
        primaryjoin="Person.id==Vehicle.person_id",
    )

    def __repr__(self):
        return f"<Person '{self.id}'>"


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.Enum(VehicleColorEnum))
    model = db.Column(db.Enum(VehicleModelEnum))
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"))

    @validates("color")
    def validate_color(self, key, color):
        if not color:
            raise AssertionError("Color is required.")

        if not VehicleColorEnum.has_value(color):
            raise AssertionError("Color not available.")

        return color

    @validates("model")
    def validate_model(self, key, model):
        if not model:
            raise AssertionError("Model is required.")

        if not VehicleModelEnum.has_value(model):
            raise AssertionError("Model not available.")

        return model

    def __repr__(self):
        return f"<Vehicle '{self.id}'>"
