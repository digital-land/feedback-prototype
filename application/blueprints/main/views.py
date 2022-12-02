from flask import Blueprint, render_template

from application.models import Organisation

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():
    organisations = Organisation.query.order_by(Organisation.name).all()
    return render_template(
        "homepage.html",
        organisations=organisations,
        page_data={"summary": {"show": True}},
    )
