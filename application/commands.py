import json
import logging
import os
import sqlite3
import tempfile

import requests
from flask.cli import AppGroup
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from application.extensions import db
from application.models import Dataset, Entity, Organisation, organisation_dataset

data_cli = AppGroup("data")

logging.basicConfig(level=logging.INFO)
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

organisation_dataset_sql = """
SELECT
    od.organisation as organisation,
    od.dataset as dataset,
    od.project as project,
    p.name as project_name,
    od.provision_reason as provision_reason,
    pr.name as provision_reason_name,
    p.project_status as project_status,
    ps.description as project_status_description,
    od.specification,
    od.notes
FROM
    organisation_dataset od,
    project p,
    project_status ps,
    provision_reason pr
WHERE od.project = p.project
AND p.project_status = ps.project_status
AND od.provision_reason = pr.provision_reason
"""

entity_sql = """
SELECT
    e.entity as entity,
    nullif(e.name, "") as name,
    nullif(e.entry_date, "") as entry_date,
    nullif(e.start_date, "") as start_date,
    nullif(e.end_date, "") as end_date,
    nullif(e.dataset, "") as dataset,
    nullif(e.json, "") as json,
    nullif(e.organisation_entity, "") as organisation_entity,
    nullif(e.prefix, "") as prefix,
    nullif(e.reference, "") as reference,
    nullif(e.geojson, "") as geojson
FROM entity e
WHERE e.dataset = '{dataset}'
AND e.organisation_entity = {organisation_entity};
"""

project_sql = """
SELECT
    project,
    description,
    name,
    project_status
FROM project;"""


@data_cli.command("load")
def load_data():

    from flask import current_app

    logger.info("loading providers")

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
    db.session.execute(stmt)
    db.session.commit()
    logger.info("finished loading providers")

    logger.info("loading datasets")

    url = f"{datasette_url}/digital-land.json?sql={dataset_sql.strip()}&_shape=array"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    stmt = insert(Dataset).values(data)
    db.session.execute(stmt)
    db.session.commit()
    logger.info("finished loading datasets")

    logger.info("loading organisation_datasets")
    url = f"{datasette_url}/digital-land.json?sql={organisation_dataset_sql.strip()}&_shape=array"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    stmt = insert(organisation_dataset).values(data)
    db.session.execute(stmt)
    db.session.commit()
    logger.info("finished loading organisation_datasets")


@data_cli.command("drop")
def drop_data():
    from application.models import Entity

    stmt = delete(Entity)
    db.session.execute(stmt)
    db.session.commit()
    stmt = delete(organisation_dataset)
    db.session.execute(stmt)
    db.session.commit()
    stmt = delete(Dataset)
    db.session.execute(stmt)
    db.session.commit()
    stmt = delete(Organisation)
    db.session.execute(stmt)
    db.session.commit()
    logger.info("all data deleted")


@data_cli.command("entities")
def load_entities():
    from flask import current_app

    from application.extensions import db

    datasette_url = current_app.config["DATASETTE_URL"]

    logger.info("loading entities")
    datasets = Dataset.query.all()
    request_data = [
        {
            "organisation": organisation.organisation,
            "organisation_entity": organisation.entity,
            "datasets": [ds.dataset for ds in datasets],
        }
        for organisation in Organisation.query.all()
    ]

    try:
        out = tempfile.NamedTemporaryFile(mode="w+b", suffix=".db", delete=False)
        sqlite_file_name = out.name
        sqlite_ = requests.get(f"{datasette_url}/entity.db", stream=True)
        for chunk in sqlite_.iter_content(chunk_size=1024):
            if chunk:
                out.write(chunk)
        out.flush()
        out.close()

        conn = sqlite3.connect(sqlite_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for item in request_data:
            logger.info(f"loading data for {item['organisation']}")
            organisation_entity = item["organisation_entity"]
            entities = []
            for dataset in item["datasets"]:
                data = cursor.execute(
                    entity_sql.format(
                        dataset=dataset, organisation_entity=organisation_entity
                    )
                )
                if data:
                    for row in data:
                        if row is not None:
                            entities.append(Entity(**_row_to_entity(row)))
                    if entities:
                        with db.session() as s:
                            s.bulk_save_objects(entities)
                            s.commit()
                            logger.info(
                                f"saved {len(entities)} {dataset} for {item['organisation']}"
                            )
                            entities = []
                else:
                    logger.info(f"no {dataset} found for {item['organisation']}")
        conn.close()
        logger.info("finished loading entities")
    finally:
        os.unlink(sqlite_file_name)


def _row_to_entity(row):
    entity = {k: v for k, v in dict(row).items() if v}
    if "json" in entity:
        entity["json"] = json.loads(entity["json"])
    if "geojson" in entity:
        entity["geojson"] = json.loads(entity["geojson"])
    return entity
