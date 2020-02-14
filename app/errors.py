from flask import render_template
from app import app1, db


@app1.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app1.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500