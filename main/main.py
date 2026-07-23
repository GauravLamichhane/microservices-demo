import os
import requests
import redis
import json as json_lib
from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
from dotenv import load_dotenv
from flask_migrate import Migrate
from producer import publish
from elasticsearch import Elasticsearch
from flask import request
from pymongo import MongoClient

es = Elasticsearch(os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200"))

mongo_client = MongoClient(os.environ.get("MONGO_URL", "mongodb://mongo:27017/"))
audit_db = mongo_client["audit_log_db"]

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

class PublishedEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    extra = db.Column(db.JSON, default=dict)
    is_consumed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

cache = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)

@app.route("/api/search")
def search():
    query = request.args.get("q", "") #grabs the value after q= so query becomes "kafka". second args if q not provided to prevent from crashing
    if not query:
        return jsonify([])
    
    result = es.search(index="products", query={
        "match_phrase_prefix": {"title": query}
    }) # match means fuzzy relevance-ranked-text
    #title says search within the title field for this search item

    hits = [
        {"id": hit["_id"], **hit["_source"]}
        for hit in result["hits"]["hits"]
    ]
    return jsonify(hits)

@app.route("/api/products")
def index():
    try:
        cached = cache.get("products")
        if cached:
            return jsonify(json_lib.loads(cached))
    except redis.exceptions.RedisError:
        print("Redis unavailable, falling back to PostgreSQL")
    products = Product.query.all()  
    result = [
        {
            "id": p.id,
            "title": p.title,
            "image": p.image,
            "likes": ProductUser.query.filter_by(product_id=p.id).count()
        }
        for p in products
    ]
    try:
        cache.setex("products", 30, json_lib.dumps(result))
    except redis.exceptions.RedisError:
        pass
    return jsonify(result)

ADMIN_API_URL = os.environ.get("ADMIN_API_URL", "http://host.docker.internal:8000")

@app.route("/api/products/<int:id>/like", methods = ['POST'])
def like(id):
    req = requests.get(f"{ADMIN_API_URL}/admin/api/user")
    print("Status:", req.status_code)
    print("Content-Type:", req.headers.get("Content-Type"))
    print("Body:", req.text)

    data = req.json()

    try:
        productUser = ProductUser(user_id = data['id'], product_id = id)
        db.session.add(productUser)
        db.session.commit()
        print("Before published")
        publish('product_liked', id)
        print(f"Publishing like for product {id}")
        cache.delete("products") # invalidate cache since like changed
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        abort(400, "You already liked this product")
    return jsonify({
        'message': 'success'
    })

@app.route("/api/audit-logs")
def audit_logs():
    limit = request.args.get("limit", default=50, type=int)
    limit = min(limit, 200)

    logs = list(
        audit_db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    )
    return jsonify(logs)
        
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

