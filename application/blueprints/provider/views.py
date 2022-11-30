from flask import Blueprint, abort, render_template
from sqlalchemy import func

from application.models import Entity, Organisation

provider = Blueprint("provider", __name__, template_folder="templates")


@provider.route("/provider/<int:entity>")
def provider_summary(entity):
    organisation = Organisation.query.filter(Organisation.entity == entity).one()
    if not organisation:
        return abort(404)

    data = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(Entity.organisation_entity == organisation.entity)
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
        organisation=organisation,
        rows=rows,
        page_data={"title": organisation.name, "summary": {"show": True}},
    )


@provider.route("/provider/<int:organisation>/dataset/<string:dataset>")
def provider_data(organisation):
    pass
