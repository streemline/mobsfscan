# -*- coding: utf_8 -*-
"""Logger Config."""
from pathlib import Path

import mobsfscan.settings as config
from mobsfscan.logger import init_logger

import yaml


logger = init_logger(__name__)


def get_config(base_path, config_file):
    options = {
        'ignore_filenames': config.IGNORE_FILENAMES,
        'ignore_extensions': config.IGNORE_EXTENSIONS,
        'ignore_paths': config.IGNORE_PATHS,
        'ignore_rules': set(),
        'severity_filter': config.SEVERITY_FILTER,
    }
    if config_file:
        cfile = Path(config_file)
    else:
        cfile = Path(base_path[0]) / config.MOBSFSCAN_CONFIG_FILE
    if cfile.is_file() and cfile.exists():
        extras = read_yaml(cfile)
        root = validate_config(extras, options)
        if not root:
            logger.warning('Invalid YAML, ignoring config from .mobsf')
            return options
        usr_ignore_files = root.get('ignore-filenames')
        usr_igonre_paths = root.get('ignore-paths')
        usr_ignore_rules = root.get('ignore-rules')
        usr_severity_filter = root.get('severity-filter')
        if usr_ignore_files:
            options['ignore_filenames'].update(usr_ignore_files)
        if usr_igonre_paths:
            options['ignore_paths'].update(usr_igonre_paths)
        if usr_ignore_rules:
            options['ignore_rules'].update(usr_ignore_rules)
        if usr_severity_filter:
            options['severity_filter'] = usr_severity_filter
    return options


def validate_config(extras, options):
    """Validate user supplied config file."""
    if not extras:
        return False
    root = extras if isinstance(extras, dict) else extras[0]
    valid = True
    for key, value in root.items():
        if key.replace('-', '_') not in options.keys():
            valid = False
            logger.warning('The config `%s` is not supported.', key)
        if not isinstance(value, list):
            valid = False
            logger.warning('The value `%s` for the config `%s` is invalid.'
                           ' Only list of value(s) are supported.', value, key)
    if not valid:
        return False
    return root


def read_yaml(file_obj, text=False):
    """Read Yaml."""
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError:
        logger.error('Failed to parse YAML')
    except Exception:
        logger.exception('Error parsing YAML')
    return None


def get_best_practices(extension):
    """Get best practices of an extension."""
    ids = set()
    all_rules = {}
    if extension == '.java':
        for yml in config.BEST_PRACTICES_DIR.rglob('*.yaml'):
            rules = read_yaml(yml)
            for rule in rules['rules']:
                all_rules[rule['id']] = rule
                ids.add(rule['id'])
    elif extension in ['.kt', '.m', '.swift']:
        if extension == '.kt':
            os_dir = config.ANDROID_RULES_DIR
            lang = 'kotlin'
        elif extension == '.m':
            os_dir = config.IOS_RULES_DIR
            lang = 'objectivec'
        elif extension == '.swift':
            os_dir = config.IOS_RULES_DIR
            lang = 'swift'
        kt = os_dir / lang / 'best_practices.yaml'
        rules = read_yaml(kt)
        for rule in rules:
            all_rules[rule['id']] = rule
            ids.add(rule['id'])
    return ids, all_rules
