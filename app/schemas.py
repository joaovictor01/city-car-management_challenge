from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import marshmallow as ma
from app.models import Person, User, Vehicle


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True


class VehicleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        include_relationships = True
        load_instance = True


class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        include_relationships = True
        load_instance = True


class PersonQueryArgsSchema(ma.Schema):
    name = ma.fields.String()
    sale_oportunity = ma.fields.Boolean()
    vehicles = ma.fields.List(ma.fields.Nested(VehicleSchema))


class VehicleQueryArgsSchema(ma.Schema):
    name = ma.fields.String()
    color = ma.fields.String()
    model = ma.fields.String()
    person_id = ma.fields.Integer()


class UserArguments(ma.Schema):
    username = ma.fields.String()
    password = ma.fields.String()
