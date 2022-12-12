import requests
from flask import Blueprint, abort, render_template, url_for
from sqlalchemy import func

from application.models import Dataset, Entity, Organisation, Resource

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
            "provider.provider_sources", organisation=organisation, dataset=dataset
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


@provider.route("/provider/<string:organisation>/<string:dataset>")
def provider_sources(organisation, dataset):
    organisation = Organisation.query.get(organisation)
    sources = [s for s in organisation.source_endpoint_datasets if s.dataset == dataset]

    return render_template(
        "sources.html",
        organisation=organisation,
        dataset=dataset,
        sources=sources,
        page_data={
            "title": f"{dataset.replace('-', ' ').capitalize()} data",
            "lede": "Provided by " + organisation.name,
        },
    )


@provider.route(
    "/provider/<string:organisation>/<string:dataset>/source/<string:source>/endpoint/<string:endpoint_id>"
)
def provider_data(organisation, dataset, source, endpoint_id):
    from flask import current_app

    datasette_url = current_app.config["DATASETTE_URL"]

    organisation = Organisation.query.get(organisation)
    dataset = Dataset.query.get(dataset)

    # param for endpoint named endpoint_id to avoid clash with builtin param name in Flask.url_for
    resources = Resource.query.filter(
        Resource.organisation == organisation.organisation,
        Resource.dataset == dataset.dataset,
        Resource.source == source,
        Resource.endpoint == endpoint_id,
    ).all()

    resource_ids = ",".join(["'" + r.resource + "'" for r in resources])
    resource_url = f"{datasette_url}/{dataset.dataset}.json"
    resource_sql = f"""
        SELECT e.*
        FROM entity e
        WHERE e.entity IN (SELECT DISTINCT(f.entity)
                                FROM fact f, fact_resource fr
                                WHERE f.fact = fr.fact
                                AND fr.resource IN ({resource_ids}))""".strip()
    params = {"sql": resource_sql, "_shape": "array"}
    response = requests.get(resource_url, params=params)
    response.raise_for_status()
    data = response.json()

    return render_template(
        "data.html",
        organisation=organisation,
        data=data,
        page_data={"title": f"{dataset.name} data"},
    )
