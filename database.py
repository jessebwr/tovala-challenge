from address import Address
from sqlalchemy.sql import func


class Database():
    """
        Class which provides a layer between the server and accessing the
        underlying sql database.

        We need 3 things to create this:
        1. Google maps client
        2. A sql database
        3. An application context
    """

    def __init__(self, client, sql_db, app):

        sql_db.init_app(app)
        sql_db.create_all(app=app)

        self.db = sql_db
        self.client = client


    def exists(self, name):
        return self.db.session.query(Address.name).filter_by(name=name).scalar() is not None

    def get_address(self, name):
        result = self.db.session.query(Address).filter_by(name=name).first()
        if result:
            return result
        else:
            return None

    def filter_by_address(self, str_address):
        result = self.db.session.query(Address).filter_by(address=str_address)
        return list(result)

    def delete_entry(self, entry):
        self.db.session.delete(entry)

    def add_entry(self, entry):
        self.db.session.add(entry)

    def commit(self):
        self.db.session.commit()


    def insert(self, name, str_address):
        # Address of the form '1313 Disneyland Dr, Anaheim, CA, USA, 92802'
        # If it doesn't exist (as verified by google), just dont insert anything

        # In some weird cases, specifically with different versions of python
        # sometimes the inputted strings are interpereted as unicode, so here
        # we're just making sure they are strings.
        name = str(name)
        str_address = str(str_address)

        if self.exists(name):
            return self.get_address(name).address

        geocode_result = self.client.geocode(str_address)
        if geocode_result:
            geocode_result = geocode_result[0]
        else:
            return False

        formatted_addr = geocode_result['formatted_address']
        lng = geocode_result['geometry']['location']['lng']
        lat = geocode_result['geometry']['location']['lat']

        address = Address(name, formatted_addr, lng, lat)
        self.add_entry(address)
        return True


    def retrieve(self, name):
        name = str(name)
        if self.exists(name):
            return self.get_address(name).address
        return None


    def retrieve_address(self, str_address):
        result = []

        str_address = str(str_address)
        geocode_result = self.client.geocode(str_address)
        if geocode_result:
            geocode_result = geocode_result[0]
        else:
            return False

        formatted_addr = geocode_result['formatted_address']
        for a in self.filter_by_address(formatted_addr):
            result.append(str(a.name))

        return result


    def update(self, name, str_address):
        # Address of the form '1313 Disneyland Dr, Anaheim, CA, USA, 92802'
        # If it doesn't exist (as verified by google), just dont insert anything
        name = str(name)
        str_address = str(str_address)

        geocode_result = self.client.geocode(str_address)
        if geocode_result:
            geocode_result = geocode_result[0]
        else:
            return False

        formatted_addr = geocode_result['formatted_address']
        lng = geocode_result['geometry']['location']['lng']
        lat = geocode_result['geometry']['location']['lat']

        # If there was something there, then return the previous one for info
        prev = None
        if self.exists(name):
            prev = self.get_address(name)
            self.delete_entry(prev)

        address = Address(name, formatted_addr, lng, lat)
        self.add_entry(address)
        self.commit()

        if prev:
            return prev.address

        # Returning True implies it wasn't there, so the update was basically
        # an insert
        return True


    def delete(self, name):
        name = str(name)
        if self.exists(name):
            result = self.get_address(name)
            self.delete_entry(result)
            self.commit()
            return result.address
        return False


    def delete_address(self, str_address):
        # Deletes all things with this address, then returns the name of
        # everything that corresponded to that address
        result = []

        str_address = str(str_address)
        geocode_result = self.client.geocode(str_address)
        if geocode_result:
            geocode_result = geocode_result[0]
        else:
            return False

        formatted_addr = geocode_result['formatted_address']
        for a in self.filter_by_address(formatted_addr):
            result.append(str(a.name))
            self.delete_entry(a)

        self.commit()
        return result


    def delete_all(self):
        self.db.session.query(Address).delete()
        self.commit()
        return True


    def calculate_centroid(self):
        total_points = self.db.session.query(Address).count()
        if total_points == 0:
            return False

        total_latitude = self.db.session.query(func.sum(Address.latitude)).scalar()
        if not total_latitude:
            total_latitude = 0.0
        total_longitude = self.db.session.query(func.sum(Address.longitude)).scalar()
        if not total_longitude:
            total_longitude = 0.0

        centroid_lat = total_latitude/total_points
        centroid_lng = total_longitude/total_points

        geocode_result = self.client.reverse_geocode((centroid_lat, centroid_lng))[0]
        return geocode_result['formatted_address']

