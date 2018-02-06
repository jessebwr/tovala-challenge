# Tovala Challenge: Centroid Calculating Database

A fairly simplistic database that takes name/address inputs, and can calculate the centroid (the central coordinates/central address) for all those points.

A playground is available at: http://jessebwr.pythonanywhere.com/

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes

### Prerequisites

You need to have pip and virtualenv installed, but these generally come when installing any new version of python.

First clone the repository, then create and activate your virtual environment.

```shell
~$ git clone https://github.com/jessebwr/tovala-challenge
~$ cd tovala-challenge
~/tovala-challenge$ virtualenv db_env
~/tovala-challenge$ source db_env/bin/activate
```

### Installing

Now, install all the requirements for the project like so:

```shell
(db_env) ~/tovala-challenge$ pip install -r requirements.txt
```

## Configuration

This runs given a sql database, so we need to configure that. This is located in db_server.cfg:

```
DEBUG=True
SQLALCHEMY_DATABASE_URI="whateversqldatabase"
SQLALCHEMY_POOL_RECYCLE=299
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

The main thing you want to replace here is the URI, some examples are:

```
mysql:
    "mysql+mysqlconnector://<username>:<password>@<address>/<database>"
    which, specifically for my online application is
    "mysql+mysqlconnector://jessebwr:imnottellingyoumypassword@jessebwr.mysql.pythonanywhere-services.com/jessebwr$default"

sqlite:
    "sqlite:////Users/jessebwr/tovala-challenge/sqlite.db"


SQLALCHEMY_DATABASE_URI="sqlite:////Users/jessebwr/tovala-challenge/sqlite.db"
```



## Running the Database Server

Now, you can start the database

```shell
(db_env) ~/tovala-challenge$ python db_server.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 254-410-876
```

You can now load up http://localhost:5000/ to see the application, where you can interact with it.

## Interacting with the Database

You can interact with the database purely from the forms on the webpage (just go to http://localhost:5000/, and use the widgets there), or you can by directly making requests to the server.

### Inserting addresses

You can insert addresses both by .csv and individually! Note that inserting a name that is already present WONT update it. 

To insert by csv:

```shell
$ curl -X POST -F "data_file=@back-end-challenge-example-data.csv" http://localhost:5000/db/api/v1.0/tasks/insert_csv
[
  {
    "name": "Mickey Mouse",
    "result": "Success"
  },
  {
    "name": "Donald Trump",
    "result": "Success"
  },
  {
    "name": "Al Capone",
    "result": "Success"
  },
  {
    "name": "Bullwinkle Moose",
    "result": "Success"
  }
]
```

It should return a list of every entry, and whether or not it was successfully inserted. Note, that the csv must be of the format:

| Name | Address1     | Address2 (usually apt number, etc.) | Country | State | City    | Zipcode |
| ---- | ------------ | ----------------------------------- | ------- | ----- | ------- | ------- |
| Jon  | 1200 Moo Dr. | Apt 4                               | USA     | FL    | Orlando | 10001   |



Now, to insert individual:
```shell
# curl http://localhost:5000/db/api/v1.0/tasks/insert/<name>/<address>

$ curl http://localhost:5000/db/api/v1.0/tasks/insert/Jesse%20Watts-Russell/4100%20Dundee%20Dr.,%20Los%20Angeles,%20CA,%20USA%2090027
{
  "result": "success"
}
```

The exact formatting of the address isn't super strict, but it does need to be something google maps would understand:
```
Probably would all work (and in reality, evaluate to the same thing):
4100 Dundee Dr., Los Angeles
4100 Dundee Dr., Los Angeles, CA 90027
4100 Dundee Dr., Los Angeles, CA, USA 90027

Probably wouldnt:
4100 Dundee
Dundee Dr., USA

I think you get the picture.
```

### Updating addresses

Pretty much the same as inserting, but it'll overwrite it if it exists.

```shell
# curl http://localhost:5000/db/api/v1.0/tasks/update/<name>/<address>

$ curl http://localhost:5000/db/api/v1.0/tasks/update/Jesse%20Watts-Russell/1342%20South%20Stanley%20Ave.,%20Los%20Angeles,%20CA%2090019
{
  "reason": "Previous address was: 4100 Dundee Dr, Los Angeles, CA 90027, USA",
  "result": "success"
}
```


### Retrieving addresses

We can retrieve addresses in two ways. The first is relatively straightforward -- given a name make a curl request like so:
```shell
# curl http://localhost:5000/db/api/v1.0/tasks/retrieve/<name>

$ curl http://localhost:5000/db/api/v1.0/tasks/retrieve/Jesse%20Watts-Russell
{
  "address": "1342 S Stanley Ave, Los Angeles, CA 90019, USA",
  "result": "success"
}
```

We can also return a list of all entries which match a certain address, given an input address:
```shell
# curl http://localhost:5000/db/api/v1.0/tasks/retrieve_address/<address>

$ curl http://localhost:5000/db/api/v1.0/tasks/retrieve_address/1342%20South%20Stanley%20Ave.,%20Los%20Angeles,%20CA%2090019
{
  "result": "success",
  "retrieved": [
    "Jesse Watts-Russell",
    "Jesse Watts-Russell2"
  ]
}
```

This will never return an error, unless the input address isn't valid. If there are no matches, it will just return an empty list.

### Deleting addresses

We can delete addresses in three ways. The first is relatively straightforward -- given a name make a curl request like so:
```shell
# curl http://localhost:5000/db/api/v1.0/tasks/delete/<name>

$ curl http://localhost:5000/db/api/v1.0/tasks/delete/Jesse%20Watts-Russell
{
  "address": "1342 S Stanley Ave, Los Angeles, CA 90019, USA",
  "result": "success"
}
```

It will also return the address that was deleted.

We can also delete all entries which match a certain address, given an input address:
```shell
# curl http://localhost:5000/db/api/v1.0/tasks/delete_address/<address>

$ curl http://localhost:5000/db/api/v1.0/tasks/delete_address/1342%20South%20Stanley%20Ave.,%20Los%20Angeles,%20CA%2090019
{
  "deleted": [
    "Jesse Watts-Russell2",
    "Jesse Watts-Russell"
  ],
  "result": "success"
}
```

It will return a list of all names for the entries that were deleted. This also will never return an error unless the input address isn't valid. If there are no matches, it'll also return just an empty list

Finally, we can just delete the whole database:
```shell
$ curl http://localhost:5000/db/api/v1.0/tasks/delete_all
{
  "result": "success"
}
```

### Calculating the centroid

Probably the easiest thing to do here, just run:
```shell
$ curl http://localhost:5000/db/api/v1.0/tasks/centroid
{
  "centroid": "1342 S Stanley Ave, Los Angeles, CA 90019, USA",
  "result": "success"
}
```

If you don't have any points/addresses, it'll just return
```
{
  "reason": "No addresses present",
  "result": "fail"
}
```


## Notes

This was built with Flask, it's pretty barebone, so I'm not doing any fancy directory structuring or anything here.

