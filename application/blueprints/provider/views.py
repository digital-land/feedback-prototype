from flask import Blueprint, abort, render_template
from sqlalchemy import func

from application.models import Entity, Organisation

provider = Blueprint("provider", __name__, template_folder="templates")


@provider.route("/provider/<int:entity>")
def provider_summary(entity):
    organisation = Organisation.query.filter(Organisation.entity == entity).one()
    if not organisation:
        return abort(404)

    project_dataset_counts = organisation.project_dataset_counts()

    other_datasets_counts = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(
            Entity.organisation_entity == organisation.entity,
            Entity.dataset.not_in([ds[0] for ds in project_dataset_counts]),
        )
        .group_by(Entity.dataset)
        .all()
    )

    project_datasets = []
    for item in project_dataset_counts:
        dataset_name = item[0].replace("-", " ").title()
        project_datasets.append(
            [
                {"text": dataset_name},
                {"text": item[1], "format": "numeric"},
            ]
        )

    other_datasets = []
    for item in other_datasets_counts:
        dataset_name = item[0].replace("-", " ").title()
        other_datasets.append(
            [
                {"text": dataset_name},
                {"text": item[1], "format": "numeric"},
            ]
        )

    return render_template(
        "provider.html",
        organisation=organisation,
        project_datasets=project_datasets,
        other_datasets=other_datasets,
        page_data={"title": organisation.name, "summary": {"show": True}},
    )


@provider.route("/provider/<int:organisation>/dataset/<string:dataset>")
def provider_data(organisation):
    pass
