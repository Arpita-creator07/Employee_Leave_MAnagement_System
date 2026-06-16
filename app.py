from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.employee_routes import employee_bp
from routes.admin_routes import admin_bp
import config
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def home():
    return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)
