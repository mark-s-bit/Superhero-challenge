from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Ensures pretty print for JSON responses.

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Welcome to the Superhero API</h1>'


api = Api(app)

class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([{
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        } for hero in heroes])

class HeroById(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return hero.to_dict(rules=('hero_powers', 'hero_powers.power'))
        return {"error": "Hero not found"}, 404

class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers])

class PowerById(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return power.to_dict()
        return {"error": "Power not found"}, 404

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return {"error": "Power not found"}, 404

        data = request.get_json()
        try:
            for attr in data:
                setattr(power, attr, data[attr])
            db.session.commit()
            return power.to_dict()
        except ValueError as e:
            return {"errors": [str(e)]}, 400

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        try:
            hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(hero_power)
            db.session.commit()
            hero = Hero.query.get(hero_power.hero_id)
            return hero.to_dict(rules=('hero_powers', 'hero_powers.power'))
        except ValueError as e:
            return {"errors": [str(e)]}, 400

api.add_resource(Heroes, '/heroes')
api.add_resource(HeroById, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerById, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
