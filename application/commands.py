import logging

import requests
from flask.cli import AppGroup
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
    url = f"{datasette_url}/digital-land.json?sql={dataset_sql.strip()}&_shape=array"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    inserts = []
    for dataset in data:
        inserts.append(
            {
                "dataset": dataset["dataset"],
                "name": dataset["name"],
                "text": dataset["text"],
            }
        )

    stmt = insert(Dataset).values(inserts)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Dataset.dataset], set_=dict(name=stmt.excluded.name)
    )
    db.session.execute(stmt)
    db.session.commit()
    print("load datasets")
