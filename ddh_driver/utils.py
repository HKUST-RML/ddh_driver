import os
import yaml


def load_ddh_config(name):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', name + '.yaml')
    print('Load configuration at %s' % os.path.abspath(config_path))
    config = {}
    with open(config_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def load_yaml(local_path):
    config_path = os.path.join(os.path.dirname(__file__), '..', local_path)
    print('Loading YAML at %s' % os.path.abspath(config_path))
    config = {}
    with open(config_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def get_abs_path(local_path):
    p = os.path.join(os.path.dirname(__file__), '..', local_path)
    return os.path.abspath(p)
