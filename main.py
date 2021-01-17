from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.orm
from cockroachdb.sqlalchemy import run_transaction


app = Flask(__name__)

app.config.from_pyfile('maid.cfg')

db = SQLAlchemy(app)

sessionmaker = sqlalchemy.orm.sessionmaker(db.engine)


class MenuItems(db.Model):
    __tablename__ = 'menuitems'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    price = db.Column(db.DECIMAL)

    def __init__(self, name, price):
        self.name = name
        self.price = price


@app.route('/menu', methods=['GET'])
def getmenu():
    menu = MenuItems.query.order_by(MenuItems.name).all()
    retval = {}
    for item in menu:
        retval[item.name] = float(item.price)
    return jsonify(items=retval)

@app.route('/menuitems', methods=["GET"])
def getmenuitems():
    menu= MenuItems.query.order_by(MenuItems.name).all()
    retval = []
    for item in menu:
        retval.append(item.name)
    retval = ", ".join(retval)
    return jsonify(items=retval)

@app.route('/menu', methods=["POST"])
def addItem():
    data = json.loads(request.data)
    if "items" in data:
        if not isinstance(data["items"], list):
            return jsonify(error = "items needs to be of type list")
        def callback(session):
            for item in data["items"]:
                if ("name" in item and "price" in item):
                    newItem = MenuItems(item["name"], item["price"])
                    session.add(newItem)
        run_transaction(sessionmaker, callback)
        return jsonify(message="success!") 
    return jsonify(error = "specify items!")


if __name__ == '__main__':
    app.run()
    #app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))