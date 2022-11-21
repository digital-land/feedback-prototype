from flask import Blueprint, abort, render_template

from application.models import Organisation

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():
    return render_template("homepage.html")


@main.route("/organisation/<string:organisation>")
def organisation(organisation):
    org = Organisation.query.get(organisation)
    if not org:
        return abort(404)

    return render_template("organisation.html", organisation=org)
