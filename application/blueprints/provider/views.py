from flask import Blueprint, abort, render_template, url_for
from sqlalchemy import func

from application.models import Entity, Organisation

provider = Blueprint("provider", __name__, template_folder="templates")


@provider.route("/provider/<string:organisation>")
def provider_summary(organisation):
    org = Organisation.query.get(organisation)
    if not org:
        return abort(404)

    project_dataset_counts = org.project_dataset_counts()

    other_datasets_counts = (
        Entity.query.with_entities(Entity.dataset, func.count(Entity.dataset))
        .filter(
            Entity.organisation_entity == org.entity,
            Entity.dataset.not_in([ds[0] for ds in project_dataset_counts]),
        )
        .group_by(Entity.dataset)
        .all()
    )

    project_datasets = []
    for item in project_dataset_counts:
        dataset = item[0]
        dataset_name = dataset.replace("-", " ").title()
        url = url_for(
            "provider.provider_data", organisation=organisation, dataset=dataset
        )
        if item[1] > 0:
            html = f"<a href='{url}'>{dataset_name}</a>"
            project_datasets.append(
                [
                    {"html": html},
                    {"text": item[1], "format": "numeric"},
                ]
            )
        else:
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
        page_data={"title": org.name, "summary": {"show": True}},
    )


@provider.route("/provider/<string:organisation>/dataset/<string:dataset>")
def provider_data(organisation, dataset):
    organisation = Organisation.query.get(organisation)
    sources = [s for s in organisation.source_endpoint_datasets if s.dataset == dataset]

    return render_template(
        "sources.html",
        organisation=organisation,
        dataset=dataset,
        sources=sources,
        page_data={"title": f"{dataset.replace('-', ' ').capitalize()} sources"},
    )
