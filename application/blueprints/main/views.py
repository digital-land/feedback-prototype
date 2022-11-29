from flask import Blueprint, render_template

from application.models import Provider

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():
    organisations = Provider.query.order_by(Provider.name).all()
    return render_template("homepage.html", organisations=organisations)
