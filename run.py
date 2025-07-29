from app.routes.app import create_app
from config import Config
from app.extensions import socketio

app = create_app()
app.config.from_object(Config)

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False)
