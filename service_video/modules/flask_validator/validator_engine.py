import sys
import traceback

from functools import wraps

from flask import current_app, request, jsonify, session

from .error_bag import ErrorBag
from .validators import validators
from .exceptions import ValidatorAttributeError, ValidatorKeyError

class ValidatorEngine(object):
  
    def __init__(self, app=None, db=None):
        self.app = app
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app, db=None):
        self.app = app
        self.db = db

    def __call__(self, validation_type, rules):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                try:
                    validation_type_method = self.__getattribute__(
                        validation_type)
                    all_validation_passes = validation_type_method(rules)
                    if not all_validation_passes:
                        return self.errors.response()
                    return func(*args, **kwargs)
                except AttributeError:
                    raise ValidatorAttributeError('AttributeError',\
                        '''%s passed, expecting json or form_data or query_string or headers''' \
                        % (validation_type))
            return inner_wrapper
        return wrapper

    def validate(self, data, validation_rules):
        self.errors = ErrorBag()
        for field, rules in validation_rules.items():
            for rule in rules:
                validator_name, validator_args = self.ruleSplitter(rule)
                try:
                    # validation_result = validators[validator_name](data.get(field, None),\
                    # validator_args[0] if len(validator_args) == 1 else validator_args)
                    validation_result = validators[validator_name](
                        data.get(field, None), *validator_args
                    )
                except KeyError:
                    raise ValidatorKeyError(
                        validator_name, 'Built-in validator specified not known')
                
                if not validation_result['status']:
                    self.errors.addError(field, validation_result['message'])
                    break

    @staticmethod
    def ruleSplitter(data):
        rules = data.split(':', 1)
        validator = rules[0]
        if not len(rules) > 1:
            return validator, []
        args = rules[1].split(',')
        return validator, tuple(args)

    def json(self, rules):
        data = request.get_json(force=True)
        self.validate(data, rules)
        if self.errors.hasErrors():
            return False
        return True

    def query_string(self, rules):
        data = request.args.to_dict()
        self.validate(data, rules)
        if self.errors.hasErrors():
            return False
        return True

    def headers(self, rules):
        data = request.headers()
        self.validate(data, rules)
        if self.errors.hasErrors():
            return False
        return True

    def form_data(self, rules):
        data = request.form
        self.validate(data, rules)
        if self.errors.hasErrors():
            return False
        return True

    def form_data_file(self, rules):
        try:
            data = request.files[rules['filename']]
            return True
        except:
            self.errors.addError(rules['filename'], 'This field is required')
            return False