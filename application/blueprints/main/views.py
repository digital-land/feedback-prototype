import string

from flask import Blueprint, render_template

from application.models import Organisation

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():
    organisations = dict.fromkeys(string.ascii_lowercase)
    for o in Organisation.query.order_by(Organisation.name).all():
        key = o.name[0].lower()
        if organisations[key] is None:
            organisations[key] = [o]
        else:
            organisations[key].append(o)

    return render_template(
        "homepage.html",
        organisations=organisations,
        page_data={"summary": {"show": True}},
    )
