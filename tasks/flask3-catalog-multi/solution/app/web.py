from flask import Flask, jsonify, request
from markupsafe import escape

from app.catalog import load_catalog
from app.encoding import CatalogJSONProvider


def create_app():
    app = Flask(__name__)
    app.json = CatalogJSONProvider(app)
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
