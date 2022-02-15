import os

basedir = os.path.abspath(os.path.dirname(__file__))

class DefaultConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
