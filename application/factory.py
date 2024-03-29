# -*- coding: utf-8 -*-
"""
Flask app factory class
"""

from flask import Flask
from flask.cli import load_dotenv

from application.filters import debug
from application.models import *  # noqa

load_dotenv()


def create_app(config_filename):
    """
    App factory function
    """
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 10
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    register_blueprints(app)
    register_context_processors(app)
    register_templates(app)
    register_filters(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_blueprints(app):
    """
    Import and register blueprints
    """

    from application.blueprints.designs.views import designs
    from application.blueprints.main.views import main
    from application.blueprints.provider.views import provider

    app.register_blueprint(main)
    app.register_blueprint(provider)
    app.register_blueprint(designs)


def register_context_processors(app):
    """
    Add template context variables and functions
    """

    def base_context_processor():
        return {"assetPath": "/static"}

    app.context_processor(base_context_processor)


def register_filters(app):
    app.jinja_env.filters["debug"] = debug
    pass


def register_extensions(app):
    from application.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app)


def register_templates(app):
    """
    Register templates from packages
    """
    from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

    multi_loader = ChoiceLoader(
        [
            app.jinja_loader,
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "digital-land-frontend": PackageLoader("digital_land_frontend"),
                }
            ),
        ]
    )
    app.jinja_loader = multi_loader


def register_commands(app):
    from application.commands import data_cli

    app.cli.add_command(data_cli)
