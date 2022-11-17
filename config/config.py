# -*- coding: utf-8 -*-
import os


class Config:
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.getenv("SECRET_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


class TestConfig(DevelopmentConfig):
    ENV = "test"
