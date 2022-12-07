import json
import logging
import os
import sqlite3
import tempfile
from datetime import datetime

import requests
from flask.cli import AppGroup
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from application.extensions import db
from application.models import (
    Dataset,
    Entity,
    Organisation,
    SourceEndpointDataset,
    organisation_dataset,
)

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
    provision_reason pr,
    dataset d
WHERE od.project = p.project
AND p.project_status = ps.project_status
AND od.provision_reason = pr.provision_reason
AND od.dataset = d.dataset;
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


source_sql = """
SELECT
    s.source,
    s.endpoint,
    e.endpoint_url,
    s.documentation_url,
    e.entry_date,
    sp.pipeline as dataset,
    o.organisation as organisation_id
FROM source s, source_pipeline sp, endpoint e, organisation o
WHERE s.source = sp.source
  AND s.endpoint = e.endpoint
  AND s.organisation = o.organisation
  AND (s.end_date is null or s.end_date == '')
  AND (
    s.organisation LIKE 'local-authority%'
    OR s.organisation LIKE 'development-corporation%'
    OR s.organisation LIKE 'national-park-authority%'
  )
  AND (s.source is not null OR s.source != '')
  AND (s.endpoint is not null OR s.endpoint != '')
  AND (sp.pipeline is not null OR sp.pipeline != '');"""


@data_cli.command("load")
def load_data():

    from flask import current_app

    datasette_url = current_app.config["DATASETTE_URL"]

    try:
        logger.info("loading organisations")
        out = tempfile.NamedTemporaryFile(mode="w+b", suffix=".db", delete=False)
        sqlite_file_name = out.name
        sqlite_ = requests.get(f"{datasette_url}/digital-land.db", stream=True)
        for chunk in sqlite_.iter_content(chunk_size=1024):
            if chunk:
                out.write(chunk)
        out.flush()
        out.close()

        conn = sqlite3.connect(sqlite_file_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        inserts = []
        organisations = cursor.execute(organisation_sql.strip())
        for org in organisations:
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
        logger.info("finished loading organisations")

        logger.info("loading datasets")
        rows = cursor.execute(dataset_sql.strip())
        datasets = [dict(row) for row in rows]
        stmt = insert(Dataset).values(datasets)
        db.session.execute(stmt)
        db.session.commit()
        logger.info("finished loading datasets")

        logger.info("loading organisation_datasets")
        rows = cursor.execute(organisation_dataset_sql.strip())
        organisation_datasets = [dict(row) for row in rows]
        stmt = insert(organisation_dataset).values(organisation_datasets)
        db.session.execute(stmt)
        db.session.commit()
        logger.info("finished loading organisation_datasets")

        logger.info("loading sources")
        rows = cursor.execute(source_sql.strip())
        data = [dict(row) for row in rows]
        for row in data:
            row["organisation_id"] = (row["organisation_id"].replace("-eng", ""),)
            if row.get("entry_date") != "":
                row["entry_date"] = datetime.strptime(
                    row.get("entry_date"), "%Y-%m-%dT%H:%M:%SZ"
                )
            else:
                row["entry_date"] = None
        stmt = insert(SourceEndpointDataset).values(data)
        db.session.execute(stmt)
        db.session.commit()
        logger.info("finished loading sources")

    except Exception as e:
        logger.exception(e)

    finally:
        os.unlink(sqlite_file_name)


@data_cli.command("drop")
def drop_data():

    stmt = delete(SourceEndpointDataset)
    db.session.execute(stmt)
    db.session.commit()

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
