from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
import requests
from producer import publish

load_dotenv()

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))


class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="user_product_unique"
        ),
    )


@app.route("/api/products")
def index():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "image": p.image,
            "likes": ProductUser.query.filter_by(product_id=p.id).count()
        }
        for p in products
    ])
@app.route("/api/products/<int:id>/like", methods = ['POST'])
def like(id):
    req = requests.get('http://host.docker.internal:8000/api/user')
    print(req.status_code)
    print(req.text)
    data = req.json()

    try:
        productUser = ProductUser(user_id = data['id'], product_id = id)
        db.session.add(productUser)
        db.session.commit()

        publish('product_liked', id)
    except:
        db.session.rollback()
        abort(400, "You already liked this product")
    return jsonify({
        'message': 'success'
    })
        
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")