# no secrets here - just local dev - anything secret goes in gitignored .env
FLASK_ENV=development
FLASK_CONFIG=config.DevelopmentConfig
FLASK_APP=application.wsgi:app
SECRET_KEY=replaceinprod
FLASK_DEBUG=1
