#This file is responsible for running the Flask application.
#It ensures that the database is created, and the app runs with debug mode enabled.


from app.db_setup import create_app

# 🔧 Create the Flask app using the factory function
app = create_app()

if __name__ == '__main__':
    """🚀 Entry point for running the Flask application.
        - Debug mode enabled for development purposes.
        - App runs on default port 5000."""
    app.run(debug=True)
