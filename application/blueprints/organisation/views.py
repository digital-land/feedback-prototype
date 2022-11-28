from flask import Blueprint, abort, render_template
from sqlalchemy import func

from application.models import Entity, Organisation

organisation = Blueprint("organisation", __name__, template_folder="templates")


@organisation.route("/organisation/<string:organisation>")
def organisation_data(organisation):
    org = Organisation.query.get(organisation)
    if not org:
        return abort(404)

    data = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(Entity.organisation_entity == org.entity)
        .group_by(Entity.dataset)
        .all()
    )
    rows = []
    for item in data:
        dataset_name = item[0].replace("-", " ").title()
        rows.append(
            [
                {"text": dataset_name},
                {"text": item[1], "format": "numeric"},
            ]
        )

    return render_template("organisation.html", organisation=org, rows=rows)
