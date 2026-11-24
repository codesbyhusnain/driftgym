from flask import Flask, escape, jsonify, request

from app.catalog import load_catalog
from app.encoding import CatalogEncoder


def create_app():
    app = Flask(__name__)
    app.json_encoder = CatalogEncoder
    app.config["JSON_SORT_KEYS"] = False
    app.config["CATALOG"] = []

    @app.before_first_request
    def load():
        app.config["CATALOG"] = load_catalog()

    @app.route("/items")
    def items():
        return jsonify(app.config["CATALOG"])

    @app.route("/items/<sku>")
    def item(sku):
        for entry in app.config["CATALOG"]:
            if entry["sku"] == sku:
                return jsonify(entry)
        return jsonify({"error": "not found"}), 404

    @app.route("/hello")
    def hello():
        return f"<p>Hello, {escape(request.args.get('name', 'world'))}!</p>"

    return app
