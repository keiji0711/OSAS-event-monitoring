from flask import Flask

import mysql.connector
from .config import Config
from.routes.AdminDashboard import bp as adminDashboard
from.routes.events import bp as Events
from.routes.reports import bp as reports
from.routes.realtime_pop import bp as realtime
from .routes.login import bp as login

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12345678'
  
    
    # Set default configuration
    app.config.from_object(Config)

    app.mysql = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )
    
    # Register blueprints
    app.register_blueprint(adminDashboard)
    app.register_blueprint(Events)
    app.register_blueprint(reports)
    app.register_blueprint(realtime)
    app.register_blueprint(login)
   
    return app
