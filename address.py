from flask_sqlalchemy import SQLAlchemy

sql_db = SQLAlchemy()

class Address(sql_db.Model):
    """
        Simple address class for a sql database
    """
    __tablename__ = "addresses"

    name = sql_db.Column(sql_db.String(100), primary_key=True)
    address = sql_db.Column(sql_db.String(4096))
    longitude = sql_db.Column(sql_db.Float)
    latitude = sql_db.Column(sql_db.Float)

    def __init__(self, name, address, longitude, latitude):
        self.name = name
        self.address = address
        self.longitude = longitude
        self.latitude = latitude
