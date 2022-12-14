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
    Organisation,
    ProvisionReason,
    Resource,
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


resource_sql = """
SELECT
    r.resource,
    s.source,
    re.endpoint,
    rd.dataset,
    ro.organisation
FROM resource r, resource_organisation ro, resource_endpoint re, resource_dataset rd, endpoint e, source s
WHERE r.resource = ro.resource
AND r.resource = re.resource
AND r.resource = rd.resource
AND re.endpoint = e.endpoint
AND e.endpoint = s.endpoint
AND (r.end_date is null OR r.end_date == '')
AND (r.end_date is null OR r.end_date == '')
AND (e.end_date is null OR e.end_date == '')
AND (s.end_date is null OR s.end_date == '')
AND (
    ro.organisation LIKE 'local-authority%'
    OR ro.organisation LIKE 'development-corporation%'
    OR ro.organisation LIKE 'national-park-authority%'
  );"""


provision_reason_sql = (
    "SELECT provision_reason, name, description FROM provision_reason;"
)


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

        logger.info("loading resources")
        rows = cursor.execute(resource_sql.strip())
        data = [dict(row) for row in rows]
        for row in data:
            row["organisation"] = row["organisation"].replace("-eng", "")
        stmt = insert(Resource).values(data)
        db.session.execute(stmt)
        db.session.commit()
        logger.info("finished loading resources")

        logger.info("loading provision reason")
        rows = cursor.execute(provision_reason_sql.strip())
        data = [dict(row) for row in rows]
        stmt = insert(ProvisionReason).values(data)
        db.session.execute(stmt)
        db.session.commit()
        logger.info("finished provision reason")

    except Exception as e:
        logger.exception(e)

    finally:
        os.unlink(sqlite_file_name)


@data_cli.command("drop")
def drop_data():

    stmt = delete(Resource)
    db.session.execute(stmt)
    db.session.commit()

    stmt = delete(SourceEndpointDataset)
    db.session.execute(stmt)
    db.session.commit()

    stmt = delete(ProvisionReason)
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


@data_cli.command("entity-numbers")
def entity_numbers():
    from flask import current_app

    datasette_url = current_app.config["DATASETTE_URL"]

    datasets = Dataset.query.all()

    sql = """SELECT DISTINCT(f.entity) AS entity
    FROM fact f, fact_resource fr
    WHERE f.fact = fr.fact
    AND fr.resource = ?"""

    for dataset in datasets:
        print(f"Checking for and processing data for {dataset.dataset}")
        try:
            sqlite_ = requests.get(f"{datasette_url}/{dataset.dataset}.db", stream=True)
            sqlite_file_name = None
            if sqlite_.status_code == 200:
                out = tempfile.NamedTemporaryFile(
                    mode="w+b", suffix=".db", delete=False
                )
                sqlite_file_name = out.name
                for chunk in sqlite_.iter_content(chunk_size=1024):
                    if chunk:
                        out.write(chunk)
                out.flush()
                out.close()

                resources = Resource.query.filter(
                    Resource.dataset == dataset.dataset
                ).all()
                for resource in resources:
                    print(
                        f"Load entity numbers for dataset {dataset.dataset} and resource {resource.resource}"
                    )
                    conn = sqlite3.connect(sqlite_file_name)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    rows = cursor.execute(sql, [resource.resource]).fetchall()
                    entities = [r["entity"] for r in rows]
                    resource.entity_numbers = [entities]
                    db.session.add(resource)
                    db.session.commit()
                    print(
                        f"Set {len(entities)} entity numbers for {resource.resource} from dataset {dataset}"
                    )
            else:
                print(f"No database at url: {datasette_url}/{dataset.dataset}.db")

        except Exception as e:
            logger.exception(e)

        finally:
            if sqlite_file_name:
                os.unlink(sqlite_file_name)
