import concurrent
import logging
import urllib.parse

import requests
from flask.cli import AppGroup
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from application.extensions import db
from application.models import Dataset, Organisation

data_cli = AppGroup("data")
logger = logging.getLogger(__name__)


organisation_sql = """
SELECT organisation, name, entity
FROM organisation WHERE
  (
    organisation LIKE 'local-authority%'
    or organisation LIKE 'development-corporation%'
    or organisation LIKE 'national-park-authority%'
  )
  AND (
    "entry_date" IS NULL
    OR "entry_date" = ""
  );
"""

dataset_sql = """
SELECT dataset, name, text
FROM dataset;
"""

# temp use only these datasets
RIPA_DATASETS = set(
    [
        "article-4-direction",
        "article-4-direction-area",
        "conservation-area",
        "listed-building",
        "listed-building-outline",
        "tree-preservation-order",
        "tree-preservation-zone",
        "tree",
    ]
)


@data_cli.command("load")
def load_data():

    from flask import current_app

    print("load organisations")
    datasette_url = current_app.config["DATASETTE_URL"]
    url = (
        f"{datasette_url}/digital-land.json?sql={organisation_sql.strip()}&_shape=array"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    inserts = []
    # remove -eng from local-authority ids until digital  land db catches up
    for org in data:
        inserts.append(
            {
                "organisation": org["organisation"].replace("-eng", ""),
                "name": org["name"],
                "entity": org["entity"],
            }
        )

    stmt = insert(Organisation).values(inserts)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Organisation.organisation], set_=dict(name=stmt.excluded.name)
    )
    db.session.execute(stmt)
    db.session.commit()
    print("load organisations done")

    print("load datasets")
    # url = f"{datasette_url}/digital-land.json?sql={dataset_sql.strip()}&_shape=array"
    # resp = requests.get(url)
    # resp.raise_for_status()
    # data = resp.json()
    # inserts = []
    # for dataset in data:
    #     inserts.append(
    #         {
    #             "dataset": dataset["dataset"],
    #             "name": dataset["name"],
    #             "text": dataset["text"],
    #         }
    #     )

    # tmp use ripa datasets only
    inserts = []
    for dataset in RIPA_DATASETS:
        inserts.append(
            {
                "dataset": dataset,
                "name": dataset.replace("-", " ").capitalize(),
            }
        )
    stmt = insert(Dataset).values(inserts)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Dataset.dataset], set_=dict(name=stmt.excluded.name)
    )
    db.session.execute(stmt)
    db.session.commit()
    print("load datasets")


@data_cli.command("drop")
def drop_data():
    stmt = delete(Dataset)
    db.session.execute(stmt)
    stmt = delete(Organisation)
    db.session.execute(stmt)
    db.session.commit()
    print("data deleted")


@data_cli.command("report")
def report():
    from flask import current_app

    datasette_url = current_app.config["DATASETTE_URL"]

    print("generate report")
    datasets = Dataset.query.all()
    request_data = [
        {"organisation": organisation, "datasets": [ds.dataset for ds in datasets]}
        for organisation in Organisation.query.all()
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(__fetch_data, datasette_url, data) for data in request_data
        }
        for future in concurrent.futures.as_completed(futures):
            print(f"The outcome is {future.result()}")


def __fetch_data(datasette_url, data):
    organisation = data["organisation"]
    datasets = data["datasets"]
    datasets_url_encoded = urllib.parse.quote(",".join(datasets))
    resp = requests.head(datasette_url)
    url = f"{datasette_url}/entity/entity.json?organisation_entity__exact={organisation.entity}&_shape=array&dataset__in={datasets_url_encoded}&_nocol=geometry_geom&_nocol=point_geom"  # noqa
    if resp.status_code == 200:
        print(f"Querying {url}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for d in data:
            print(d)
    else:
        print("No data")
    return f"Done fetching data for {organisation.organisation}"
