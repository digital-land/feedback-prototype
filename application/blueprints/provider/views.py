import requests
from flask import Blueprint, abort, render_template, url_for
from sqlalchemy import text

from application.extensions import db
from application.models import (
    Dataset,
    Organisation,
    ProvisionReason,
    Resource,
    SourceEndpointDataset,
)

provider = Blueprint("provider", __name__, template_folder="templates")


provider_source_sql = text(
    """SELECT
    od.organisation,
    d.name, d.dataset,
    od.project,
    od.provision_reason,
    od.provision_reason_name,
    count(s.source) as number_of_sources
FROM  organisation_dataset od
LEFT JOIN source_endpoint_dataset s
ON (od.dataset = s.dataset and od.organisation = s.organisation_id)
JOIN dataset d on (od.dataset = d.dataset)
WHERE od.organisation = :organisation
GROUP BY od.organisation, d.name, d.dataset, od.project, od.provision_reason, od.provision_reason_name
ORDER BY d.name, od.project, od.provision_reason_name"""
)


ordered_provision_reasons = [
    "statutory",
    "expected",
    "encouraged",
    "prospective",
    "authoritative",
    "alternative",
]


# TODO @PaulSmith - override the provision reason copy here
provision_reason_copy = {
    "statutory": "Data this organisation has a statutory duty to provide complying to a legislated standard.",
    "expected": """Data this organisation is expected to provide because they have agreed to as
    a member of the project developing the specification.""",
    "encouraged": "The organisation is encouraged to provide data to this standard",
    "prospective": "Data this organisation could publish to a specification currently being developed.",
    "authoritative": "The organisation is the authoritative source of this data",
    "alternative": "The organisation provides this data",
}


@provider.route("/provider/<string:organisation>")
def summary(organisation):
    org = Organisation.query.get(organisation)
    if not org:
        return abort(404)

    provision_reasons = []
    for p in ordered_provision_reasons:
        provision_reasons.append(ProvisionReason.query.get(p))

    with db.session() as session:
        sources = session.execute(
            provider_source_sql, {"organisation": org.organisation}
        ).fetchall()

    sources_by_provision_reason = {}
    for p in provision_reasons:
        groups = []
        for s in sources:
            if s.provision_reason == p.provision_reason:
                # print(p.provision_reason)
                name = {"text": s.name}
                url = url_for(
                    "provider.sources",
                    organisation=s.organisation,
                    dataset=s.dataset,
                )
                html_link = f"<a href='{url}'>Collection report</a>"
                feedback_link = {"html": html_link, "format": "numeric"}

                if s.number_of_sources > 0:
                    name = {"html": f"{s.name}"}
                    html = f"<a href='{url}'>{s.number_of_sources} source"
                    html += ("s" if s.number_of_sources > 1 else "") + "</a>"
                    number_of_sources = {"html": html}

                else:
                    html = f"""<span class='govuk-tag
                    {'govuk-tag--red'
                    if p.provision_reason == 'statutory' or p.provision_reason == 'expected'
                    else 'govuk-tag--blue' }'
                    title='There are no data sources for this dataset'>0 Sources</span>"""
                    number_of_sources = {
                        "html": html,
                    }

                groups.append((name, number_of_sources, feedback_link))
        sources_by_provision_reason[p.provision_reason] = groups

    return render_template(
        "provider.html",
        organisation=organisation,
        sources_by_provision_reason=sources_by_provision_reason,
        provision_reasons=provision_reasons,
        provision_reason_copy=provision_reason_copy,
        page_data={
            "title": org.name,
            "caption": "Data provider",
            "summary": {"show": True},
        },
    )


@provider.route("/provider/<string:organisation>/<string:dataset>")
def sources(organisation, dataset):
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
def data(organisation, dataset, source, endpoint_id):
    from flask import current_app

    datasette_url = current_app.config["DATASETTE_URL"]

    organisation = Organisation.query.get(organisation)
    dataset = Dataset.query.get(dataset)
    endpoint = (
        SourceEndpointDataset.query.with_entities(SourceEndpointDataset.endpoint_url)
        .filter(SourceEndpointDataset.endpoint == endpoint_id)
        .first()
    )
    endpoint_url = endpoint["endpoint_url"]
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
        dataset=dataset,
        endpoint_url=endpoint_url,
        page_data={"title": "Data source", "lede": f"provided by {organisation.name}"},
    )
