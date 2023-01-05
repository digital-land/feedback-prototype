import string

from flask import Blueprint, render_template

from application.models import Organisation

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():

    organisations = Organisation.query.order_by(Organisation.name).all()
    organisations_by_letter = dict.fromkeys(string.ascii_lowercase, [])
    for o in organisations:
        key = o.name[0].lower()
        organisations_by_letter[key].append(o)

    return render_template(
        "homepage.html",
        organisations=organisations,
        page_data={"summary": {"show": True}},
    )
