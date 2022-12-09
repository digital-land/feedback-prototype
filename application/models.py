from sqlalchemy.dialects.postgresql import JSON

from application.extensions import db

organisation_dataset = db.Table(
    "organisation_dataset",
    db.Column("organisation", db.ForeignKey("organisation.organisation")),
    db.Column("dataset", db.ForeignKey("dataset.dataset")),
    db.Column("project", db.Text),
    db.Column("project_name", db.Text),
    db.Column("provision_reason", db.Text),
    db.Column("provision_reason_name", db.Text),
    db.Column("project_status", db.Text),
    db.Column("project_status_description", db.Text),
    db.Column("specification", db.Text),
    db.Column("notes", db.Text),
)


class Organisation(db.Model):
    organisation = db.Column(db.Text, primary_key=True, nullable=False)
    entity = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    entities = db.relationship("Entity", back_populates="organisation")
    datasets = db.relationship(
        "Dataset", secondary=organisation_dataset, back_populates="organisations"
    )
    source_endpoint_datasets = db.relationship(
        "SourceEndpointDataset", back_populates="organisation"
    )

    def project_dataset_counts(self):
        data = []
        for dataset in self.datasets:
            count = (dataset.dataset, len(self.get_entity_by_dataset(dataset.dataset)))
            data.append(count)
        return data

    def get_entity_by_dataset(self, dataset):
        return [entity for entity in self.entities if entity.dataset == dataset]


class Dataset(db.Model):
    dataset = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=True)
    organisations = db.relationship(
        "Organisation", secondary=organisation_dataset, viewonly=True
    )


class Entity(db.Model):
    entity = db.Column(db.BigInteger, primary_key=True, nullable=False)
    dataset = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    entry_date = db.Column(db.Date)
    geojson = db.Column(JSON)
    json = db.Column(JSON)
    name = db.Column(db.Text)
    prefix = db.Column(db.Text)
    reference = db.Column(db.Text)
    organisation_entity = db.Column(db.BigInteger, db.ForeignKey("organisation.entity"))
    organisation = db.relationship("Organisation", back_populates="entities")


class SourceEndpointDataset(db.Model):
    source = db.Column(db.Text, primary_key=True, nullable=False)
    endpoint = db.Column(db.Text, primary_key=True, nullable=False)
    dataset = db.Column(db.Text, primary_key=True, nullable=False)
    endpoint_url = db.Column(db.Text, nullable=False)
    documentation_url = db.Column(db.Text, nullable=True)
    entry_date = db.Column(db.Date)
    organisation_id = db.Column(
        db.Text, db.ForeignKey("organisation.organisation"), nullable=False
    )
    organisation = db.relationship(
        "Organisation", back_populates="source_endpoint_datasets"
    )


class Resource(db.Model):
    resource = db.Column(db.Text, nullable=False, primary_key=True)
    source = db.Column(db.Text, nullable=False, primary_key=True)
    endpoint = db.Column(db.Text, nullable=False, primary_key=True)
    dataset = db.Column(db.Text, nullable=False, primary_key=True)
    organisation = db.Column(db.Text, nullable=False, primary_key=True)
