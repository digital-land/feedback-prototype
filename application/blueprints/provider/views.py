from flask import Blueprint, abort, render_template
from sqlalchemy import func

from application.models import Entity, Organisation

provider = Blueprint("provider", __name__, template_folder="templates")


@provider.route("/provider/<string:organisation>")
def provider_summary(organisation):
    org = Organisation.query.filter(Organisation.entity == organisation).one()
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

    return render_template(
        "provider.html",
        organisation=org,
        rows=rows,
        page_data={"title": org.name, "summary": {"show": True}},
    )


@provider.route("/provider/<string:organisation>/dataset/<string:dataset>")
def provider_data(organisation):
    pass
