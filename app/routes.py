from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import create_access_token, jwt_required
from flask_smorest import Blueprint, abort
from loguru import logger

from app.extensions import db
from app.models import Person, User, Vehicle
from app.schemas import (
    PersonQueryArgsSchema,
    PersonSchema,
    UserArguments,
    UserSchema,
    VehicleQueryArgsSchema,
    VehicleSchema,
)

body = {
    "name": "Authorization",
    "in": "header",
    "description": "Authorization: Bearer <access_token>",
    "required": "true",
    "default": "nothing",
}

bp = Blueprint("api", __name__, url_prefix="/api", description="Car Management API")


# User registration route
@bp.route("/register")
class Register(MethodView):
    @bp.arguments(UserArguments)
    @bp.response(201, UserSchema)
    @bp.doc(description="Create a new user")
    def post(self, user_data):
        """Create a new user"""
        if User.query.filter_by(username=user_data.get("username")).first():
            abort(409, message="User already exists")
        user = User(username=user_data.get("username"))
        user.set_password(user_data.get("password"))
        db.session.add(user)
        db.session.commit()
        return user


# User login route
@bp.route("/login")
class Login(MethodView):
    @bp.arguments(UserArguments)
    @bp.response(200, content_type="application/json")
    def post(self, login_data):
        data = request.get_json()
        user = User.query.filter_by(username=login_data.get("username")).first()

        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200
        else:
            abort(401, message="Invalid username or password")


# Get all people
@bp.route("/people")
class PeopleListResource(MethodView):
    @jwt_required()
    @bp.response(200, PersonSchema(many=True))
    @bp.doc(description="Get all people with their vehicles")
    @bp.doc(parameters=[body])
    def get(self):
        """Get all people with their vehicles"""
        return Person.query.all()

    @jwt_required()
    @bp.arguments(PersonQueryArgsSchema)
    @bp.response(201, PersonSchema)
    @bp.doc(description="Add a new person")
    @bp.doc(parameters=[body])
    def post(self, person_data):
        """Create a new person"""
        person = Person(
            name=person_data.get("name"),
            sale_oportunity=person_data.get("sale_oportunity"),
        )
        try:
            db.session.add(person)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Error adding person: {e}")
            abort(400, message="Error adding person.")
        return person


# Get or add vehicles to a person
@bp.route("/vehicles/person/<int:person_id>")
class PersonVehiclesResource(MethodView):
    @jwt_required()
    @bp.response(200, PersonSchema)
    def get(self, person_id):
        """Get a person by ID with their vehicles"""
        person = Person.query.get_or_404(person_id)
        return person.vehicles.all()

    @jwt_required()
    @bp.arguments(VehicleQueryArgsSchema)
    @bp.response(201, VehicleSchema)
    @bp.doc(
        description=(
            "Add a new vehicle to a person (max 3 vehicles) with color "
            "(yellow, blue, gray) and model (hatch, sedan, convertible)"
        )
    )
    def post(self, vehicle_data, person_id):
        """Add a vehicle to a person (max 3 vehicles)"""
        person = Person.query.get_or_404(person_id)
        if not person.sale_oportunity:
            abort(403, message="Person cannot buy vehicles yet.")
        if len(person.vehicles.all()) >= 3:
            abort(400, message="A person can only have up to 3 vehicles.")
        try:
            vehicle = Vehicle(
                name=vehicle_data.get("name"),
                color=vehicle_data.get("color"),
                model=vehicle_data["model"],
                person_id=person_id,
            )
            db.session.add(vehicle)
            db.session.commit()
            return vehicle
        except Exception as e:
            logger.warning(f"Error adding vehicle: {e}")
            abort(400, message=str(e))


@bp.route("/vehicle/<int:vehicle_id>/person/<int:person_id>")
class PersonVehicleResource(MethodView):

    @jwt_required()
    @bp.response(200, VehicleSchema)
    @bp.doc(description="Get vehicle information")
    def get(self, vehicle_id, person_id):
        """Add a vehicle to a person (max 3 vehicles)"""
        if not Vehicle.query.get_or_404(vehicle_id):
            abort(404, message="Vehicle not found.")
        if not Vehicle.query.get_or_404(vehicle_id).person_id == person_id:
            abort(403, message="Vehicle does not belong to person.")
        try:
            return Vehicle.query.get_or_404(vehicle_id)
        except Exception as e:
            logger.warning(e)
            abort(400, message="Error deleting vehicle.")

    @jwt_required()
    @bp.response(204)
    @bp.doc(description="Delete a vehicle from a person")
    def delete(self, vehicle_id, person_id):
        """Add a vehicle to a person (max 3 vehicles)"""
        if not Vehicle.query.get_or_404(vehicle_id):
            abort(404, message="Vehicle not found.")
        if not Vehicle.query.get_or_404(vehicle_id).person_id == person_id:
            abort(403, message="Vehicle does not belong to person.")
        try:
            db.session.delete(Vehicle.query.get_or_404(vehicle_id))
            db.session.commit()
        except Exception as e:
            logger.warning(e)
            abort(400, message="Error deleting vehicle.")


@bp.route("/person/<int:person_id>")
class PersonById(MethodView):
    @jwt_required()
    @bp.response(200, PersonSchema)
    def get(self, person_id):
        person = Person.query.get_or_404(person_id)
        return person

    @jwt_required()
    @bp.response(204)
    def delete(self, person_id):
        person = Person.query.get_or_404(person_id)
        db.session.delete(person)
        db.session.commit()
        return "", 204

    @jwt_required()
    @bp.arguments(PersonQueryArgsSchema(partial=True))
    @bp.response(200, PersonSchema)
    @bp.doc(description="Edit a person")
    def patch(self, data, person_id):
        person = Person.query.get_or_404(person_id)
        data = request.get_json()
        if data.get("name"):
            person.name = data.get("name")
        if data.get("sale_oportunity"):
            person.sale_oportunity = data.get("sale_oportunity")
        db.session.add(person)
        db.session.commit()

        return person
