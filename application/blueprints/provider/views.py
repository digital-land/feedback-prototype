from flask import Blueprint, abort, render_template
from sqlalchemy import func

from application.models import Entity, Organisation

provider = Blueprint("provider", __name__, template_folder="templates")


@provider.route("/provider/<int:entity>")
def provider_summary(entity):
    organisation = Organisation.query.filter(Organisation.entity == entity).one()
    if not organisation:
        return abort(404)

    organisation_datasets = [ds.dataset for ds in organisation.datasets]

    project_dataset_counts = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(
            Entity.organisation_entity == organisation.entity,
            Entity.dataset.in_(organisation_datasets),
        )
        .group_by(Entity.dataset)
        .all()
    )
    datasets_found = [item[0] for item in project_dataset_counts]
    for ds in organisation_datasets:
        if ds not in datasets_found:
            project_dataset_counts.append((ds, 0))

    project_dataset_counts.sort(key=lambda x: x[0])

    other_datasets_counts = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(
            Entity.organisation_entity == organisation.entity,
            Entity.dataset.not_in(organisation_datasets),
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
