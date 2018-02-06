#!db_env/bin/python
from flask import Flask, jsonify, request, render_template
from address import sql_db
from database import Database
import googlemaps, io, csv

app = Flask(__name__)
app.config.from_pyfile("db_server.cfg")

gmaps = googlemaps.Client(key='AIzaSyATTpiwzNG30LG-dYTg5Gj8yNhrY06lIuc')
db = Database(gmaps, sql_db, app)

@app.route('/')
def index():
    return render_template('index.html')

def insert_base(name, address):
    if not name or not address:
        return jsonify({'result' : 'fail', 'reason' : 'Invalid name or address'})

    result = db.insert(name, address)
    json_result = None
    if result == True:
        db.commit()
        json_result = {'result' : 'success'}
    elif result == False:
        json_result = {'result' : 'fail', 'reason' : 'Invalid name or address'}
    else:
        json_result = {'result' : 'fail', 'reason' : 'Already present, current address:' + str(result)}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/insert/<string:name>/<string:address>', methods=['GET'])
def insert(name, address):
    return insert_base(name, address)

@app.route('/db/api/v1.0/tasks/insert', methods=['POST'])
def insert_with_form():
    name = request.form['name']
    address = request.form['address']
    return insert_base(name, address)

@app.route('/db/api/v1.0/tasks/insert_csv', methods=['POST', 'PUT'])
def insert_csv():
    f = request.files['data_file']
    if not f:
        result = {'result' : 'fail', 'reason' : 'No file'}
        return jsonify(result)

    try:
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input)
        results = []
        for row in csv_input:
            # Create the entry
            name = row[0]
            address = row[1] + " " + row[2] + ", " + row[5] + ", " + \
                      row[4] + ", " + row[3] + " " + row[6]
            result = db.insert(name, address)
            if result == True:
                results.append({'name' : name, 'result' : 'Success'})
            elif result == False:
                results.append({'name' : name, 'result' : 'fail', 'reason' : 'Invalid name or address'})
            else:
                results.append({'name' : name, 'result' : 'fail', \
                                'reason' : 'Already present, current address: ' + str(result)})
        db.commit()
        return jsonify(results)
    except Exception as e:
        print(e)
        result = {'result' : 'fail', 'reason' : 'Invalid file'}
        return jsonify(result)



def update_base(name, address):
    if not name or not address:
        return jsonify({'result' : 'fail', 'reason' : 'Invalid name or address'})


    result = db.update(name, address)
    json_result = None
    if result == True:
        db.commit()
        json_result = {'result' : 'success', 'reason' : 'No previous entry'}
    elif result == False:
        json_result = {'result' : 'fail', 'reason' : 'Invalid name or address'}
    else:
        json_result = {'result' : 'success', 'reason' : 'Previous address was: ' + result}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/update/<string:name>/<string:address>', methods=['GET'])
def update(name, address):
    return update_base(name, address)

@app.route('/db/api/v1.0/tasks/update', methods=['POST'])
def update_with_form():
    name = request.form['name']
    address = request.form['address']
    return update_base(name, address)


def retrieve_base(name):
    result = db.retrieve(name)
    json_result = None
    if not result:
        json_result = {'result' : 'fail', 'reason' : 'Name not in database'}
    else:
        json_result = {'result' : 'success', 'address' : str(result)}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/retrieve/<string:name>', methods=['GET'])
def retrieve(name):
    return retrieve_base(name)

@app.route('/db/api/v1.0/tasks/retrieve', methods=['POST'])
def retrieve_with_form():
    name = request.form['name']
    return retrieve_base(name)


def retrieve_address_base(address):
    result = db.retrieve_address(address)
    json_result = None
    if result == False:
        json_result = {'result' : 'fail', 'reason' : 'Invalid name or address'}
    else:
        json_result = {'result' : 'success', 'retrieved' : result}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/retrieve_address/<string:address>', methods=['GET'])
def retrieve_address(address):
    return retrieve_address_base(address)

@app.route('/db/api/v1.0/tasks/retrieve_address', methods=['POST'])
def retrieve_address_with_form():
    address = request.form['address']
    return retrieve_address_base(address)



def delete_base(name):
    result = db.delete(name)
    json_result = None
    if not result:
        json_result = {'result' : 'fail', 'reason' : 'Name not in database'}
    else:
        json_result = {'result' : 'success', 'address' : str(result)}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/delete/<string:name>', methods=['GET'])
def delete(name):
    return delete_base(name)

@app.route('/db/api/v1.0/tasks/delete', methods=['POST'])
def delete_with_form():
    name = request.form['name']
    return delete_base(name)


def delete_address_base(address):
    result = db.delete_address(address)
    json_result = None
    if result == False:
        json_result = {'result' : 'fail', 'reason' : 'Invalid name or address'}
    else:
        json_result = {'result' : 'success', 'deleted' : result}
    return jsonify(json_result)

@app.route('/db/api/v1.0/tasks/delete_address/<string:address>', methods=['GET'])
def delete_address(address):
    return delete_address_base(address)

@app.route('/db/api/v1.0/tasks/delete_address', methods=['POST'])
def delete_address_with_form():
    address = request.form['address']
    return delete_address_base(address)


@app.route('/db/api/v1.0/tasks/delete_all', methods=['GET'])
def delete_all():
    db.delete_all()
    return jsonify({'result' : 'success'})


@app.route('/db/api/v1.0/tasks/centroid', methods=['GET'])
def centroid():
    result = db.calculate_centroid()
    json_result = None
    if not result:
        json_result = {'result' : 'fail', 'reason' : 'No addresses present'}
    else:
        json_result = {'result' : 'success', 'centroid' : result}
    return jsonify(json_result)

if __name__ == '__main__':
    app.run(debug=True)
