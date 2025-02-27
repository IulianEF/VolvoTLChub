from app.tests.performance_tests import performance_tests
from app import app


app.register_blueprint(performance_tests, url_prefix='/tests')