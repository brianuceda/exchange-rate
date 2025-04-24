from flask_cors import CORS

def configure_cors(app, origins):
    CORS(app, resources={r"/api/*": {
        "origins": origins,
        "methods": ["GET"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }})
    
    return app
