from flask import Flask
from flask_cors import CORS
from app.routes.legal import legal_bp


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(legal_bp, url_prefix="/api/legal")

    @app.route("/ping", methods=["GET"])
    def ping():
        return {"message": "pong"}, 200

    @app.route("/")
    def home():
        return {"status": "Legal AI Backend Running"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
