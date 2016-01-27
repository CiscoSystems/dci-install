__author__ = 'brdemers'

import logging
import ConfigParser
import os

class Config(object):
    """Config wrapper that will parse an ini file and convert strings that look like objects into dicts, and lists"""

    logger = logging.getLogger("config")

    def __init__(self, config_file, osp_version, location='sj', override_args={}):
        self.config = self._read_config(config_file, osp_version, location, override_args)

    def get(self, key):
        """Gets property from config.

        :param key: dictionary key used to find a value
        :return: value corresponding to key.
        """
        return self.config.get(key)

    def _read_config(self, config_file, osp_version, location, override_args):
        """Parse config, values that appear to be python snippets will also be evaluated.

        For example, any config string starting with '{' or '[' will be eval'd.

        :param config_file: Config file to parse.
        :param location: short lab location name ['sj', 'bxb']
        :param override_args: args that will override anything config files.
        :return: dict representing all of the configuration.
        """

        module_dir = os.path.dirname(os.path.abspath(__file__))
        common_conf_dir = os.path.join(module_dir, 'conf_common')
        location_conf = os.path.join(common_conf_dir, location + '.conf')
        base_conf = os.path.join(common_conf_dir, 'base.conf')
        osp_version_conf = os.path.join(common_conf_dir, 'osp{0}.conf'.format(osp_version))
        user_conf = os.path.join(os.path.expanduser('~'), '.osp7-installer', 'osp7.conf')

        config_parser = ConfigParser.SafeConfigParser()
        config_files_to_read = [base_conf, osp_version_conf, location_conf, user_conf, config_file]
        actual_config_files = config_parser.read(config_files_to_read)
        self.logger.debug("Config loaded from files: " + str(actual_config_files))
        config = {}

        for section in config_parser.sections():
            options = config_parser.options(section)

            section_dict = {}
            for option in options:
                value = config_parser.get(section, option).strip()
                section_dict[option] = value

            # for each section look look for override args
            for key, value in override_args.iteritems():
                # override all keys in format of section.key
                if key.startswith(section+'.'):
                    new_key = key.replace(section+'.', '', 1)
                    section_dict[new_key] = value
                # override all properties if they do NOT contain a "."
                elif "." not in key:
                    section_dict[key] = value


            # now parse bools, and maps from args
            for key, value in section_dict.iteritems():
                if value in ["True", "true", "yes"]:
                    value = True
                elif value in ["False", "false", "no"]:
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.startswith('[') or value.startswith('{'):
                    value = eval(value)

                section_dict[key] = value

            config[section] = section_dict

        self.logger.debug("config: {}".format(config))
        return config
