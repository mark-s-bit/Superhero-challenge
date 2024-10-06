from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Custom naming convention for SQLAlchemy
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)

# Hero Model
class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'  # Fixed incorrect tablename variable

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)  # Added nullable=False to enforce input
    super_name = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power')

    # Serialization rules to avoid recursive loops
    serialize_rules = ('-hero_powers.hero', '-powers.heroes')

    # Representation for better debug output
    def __repr__(self):
        return f'<Hero {self.id}, Name: {self.name}, Super Name: {self.super_name}>'


# Power Model
class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero')

    # Serialization rules to avoid recursive loops
    serialize_rules = ('-hero_powers.power', '-heroes.powers')

    # Validate description to ensure it is at least 20 characters long
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    # Representation for better debug output
    def __repr__(self):
        return f'<Power {self.id}, Name: {self.name}>'


# HeroPower Model (junction table)
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Foreign Keys
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Serialization rules to avoid recursive loops
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # Validate strength to ensure it's one of the valid options
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be one of: 'Strong', 'Weak', or 'Average'")
        return strength

    # Representation for better debug output
    def __repr__(self):
        return f'<HeroPower {self.id}, Strength: {self.strength}>'
