"""Songs REST service backed by MongoDB."""
import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from bson import json_util
from flask import jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from . import app

host = os.environ.get("MONGODB_SERVICE", "127.0.0.1")
port = os.environ.get("MONGODB_PORT", "27017")
username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")
credentials = ""
if username and password:
    credentials = f"{quote_plus(username)}:{quote_plus(password)}@"
authority = host if ":" in host else f"{host}:{port}"
uri = os.environ.get("MONGODB_URI", f"mongodb://{credentials}{authority}/?authSource=admin")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client[os.environ.get("MONGODB_DATABASE", "songs")]
db.songs.create_index("id", unique=True)
if db.songs.count_documents({}) == 0:
    seed = json.loads((Path(__file__).parent / "data" / "songs.json").read_text())
    db.songs.insert_many(seed)

def parse_json(value):
    return json.loads(json_util.dumps(value))

@app.route("/health")
def health():
    client.admin.command("ping")
    return jsonify(status="OK"), 200

@app.route("/count")
def count():
    return jsonify(count=db.songs.count_documents({})), 200

@app.route("/song", methods=["GET"])
def get_songs():
    return jsonify(songs=parse_json(list(db.songs.find({})))), 200

@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    song = db.songs.find_one({"id": id})
    if song is None:
        return {"message": f"song with id {id} not found"}, 404
    return parse_json(song), 200

@app.route("/song", methods=["POST"])
def create_song():
    song = request.get_json(silent=True)
    if not isinstance(song, dict) or type(song.get("id")) is not int:
        return {"message": "song must include an integer id"}, 400
    song.pop("_id", None)
    try:
        result = db.songs.insert_one(song)
    except DuplicateKeyError:
        return {"Message": f"song with id {song['id']} already present"}, 302
    return {"inserted id": parse_json(result.inserted_id)}, 201

@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    changes = request.get_json(silent=True)
    if not isinstance(changes, dict) or changes.get("id", id) != id:
        return {"message": "song must be an object with an id matching the URL"}, 400
    changes.pop("_id", None)
    result = db.songs.update_one({"id": id}, {"$set": changes})
    if result.matched_count == 0:
        return {"message": "song not found"}, 404
    if result.modified_count == 0:
        return {"message": "song found, but nothing updated"}, 200
    return parse_json(db.songs.find_one({"id": id})), 201

@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    result = db.songs.delete_one({"id": id})
    if result.deleted_count == 0:
        return {"message": "song not found"}, 404
    return "", 204
