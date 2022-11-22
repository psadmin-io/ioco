# ioco utilities 

import os
import sys
import logging
import json
import datetime
from pathlib import Path

this = sys.modules[__name__]
this.config = None
this.timings = None
this.total_time_key = 'TOTAL TIME'
this.timings_printed = False

def __merge(dict_1, dict_2):     
    """Merge two dictionaries.     
    Values that evaluate to true take priority over falsy values.     
    `dict_1` takes priority over `dict_2`.
    """
    return dict((str(key), dict_1.get(key) or dict_2.get(key))
        for key in set(dict_2) | set(dict_1))

def get_config(args):
    
    config = args
    
    # Environment variable overrides
    config['--home'] = os.getenv('IOCO_HOME',args['--home'])
    config['--conf'] = os.getenv('IOCO_CONF',args['--conf'])
    config['--logs'] = os.getenv('IOCO_LOGS',args['--logs'])
    config['--cust-yaml'] = os.getenv('IOCO_YAML',args['--cust-yaml'])
    config['--verbose'] = os.getenv('IOCO_VERBOSE',args['--verbose'])
    config['--force'] = os.getenv('IOCO_FORCE',args['--force'])

    if not args['--home']:
        config['--home'] = '/u01/app/ioco'

    if not args['--conf']:
        config['--conf'] = config['--home'] + '/conf.json'    
    
    if not args['--logs']:
        config['--logs'] = config['--home'] + '/logs'    

    if not args['--cust-yaml']:
        config['--cust-yaml'] = config['--home'] + '/dpk/psft_customizations.yaml'    

    # JSON config
    try:
        with open(config['--conf']) as json_file:
            config = __merge(config, json.load(json_file))
    except FileNotFoundError:
        pass
    except:
        # logging - needs good message for invalid json errors
        raise    
    
    # Defaults
    default_config = {
        'mainlog': 'ioco.log',
        'patch_id': None,
        'psft_base_dir': '/u01/app/oracle/product',
        'download_threads': 5,
        'cm_dpk_files_dir': '/cm_psft_dpks',
        '--block-disk': '/dev/oracleoci/oraclevdb',
        '--block-path': '/u01/app/oracle/product',
        '--mount-path': '/cm_psft_dpks',
        '--dpk-source': 'CM',
        '--dpk-platform': 'linux',
        '--quiet': False
    }
    config = __merge(config, default_config)
    logging.debug("Merged Config File: " + str(config))

    # Defaults - response.cfg
    default_config = {
        'db_name': 'PSFTDB',
        'db_host': 'localhost',
        'pia_port': '8000',
        'opr_id': 'PS',
        'opr_pwd': 'PS',
        'gw_user_pwd': 'password',
        'webprofile_user_pwd': 'PTWEBSERVER',
        'weblogic_admin_pwd': 'Passw0rd#',
        'access_pwd': 'SYSADM',
        'admin_pwd': 'Passw0rd_',
        'connect_pwd': 'peop1e',
        'gw_keystore_pwd': 'password'
    }
    
    # Check default admin user
    if config['--dpk-type'] in ['FSCM','IH']:
        default_config['opr_id'] = 'VP1'
        default_config['opr_pwd'] = 'VP1'

    config = __merge(config, default_config)

    # More Defaults
    default_config = {
        '--example-path': config['--home'] + '/examples',
        'dpk_files_dir': config['--home'] + '/dpk',
        'dpk_deploy_dir': config['psft_base_dir'] + '/dpk', 
        'user_home_dir': '/home',
        'ps_cfg_dir': config['psft_base_dir'] + '/hostname/ps_cfg_home',
        'db_service_name': config['db_name']
    }
    config = __merge(config, default_config)
    this.config = config

    return config

def setup_home(config):
    Path(config['--home']).mkdir(parents=True, exist_ok=True) 
    Path(config['--logs']).mkdir(parents=True, exist_ok=True) 
    Path(config['--example-path']).mkdir(parents=True, exist_ok=True) 

def setup_logging(config):
    if config['--verbose']:
        loglevel=logging.DEBUG
    else:
        loglevel=logging.INFO
    
    rootLogger = logging.getLogger()
    rootLogger.setLevel(loglevel)

    fileHandler = logging.FileHandler('{0}/{1}'.format(config['--logs'], config['mainlog']))
    fileFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
    fileHandler.setFormatter(fileFormatter)
    fileHandler.setLevel(loglevel)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleFormatter = logging.Formatter('[%(levelname)-5.5s]  %(message)s')
    consoleHandler.setFormatter(consoleFormatter)
    consoleHandler.setLevel(loglevel)
    rootLogger.addHandler(consoleHandler)

    logging.debug('log: ' + config['--logs'] + '/' + config['mainlog'])

def generate_full_config_file():
    pass

def init_timings():
    this.timings = {}
    this.timings[this.total_time_key] = datetime.datetime.now()

def start_timing(name):
    this.timings[name] = datetime.datetime.now()

def end_timing(name):
    # if timing duration has been calculated, skip
    if not isinstance(this.timings[name], datetime.timedelta):
        start_time = this.timings[name]
        this.timings[name] = datetime.datetime.now() - start_time

def error_timings(name):
    end_timing(name)
    print_timings()

def print_timings():

    if not this.timings_printed and not this.config['--quiet']:

        # if total time has been calculated by a previous call, skip
        if not isinstance(this.timings[this.total_time_key], datetime.timedelta): 
            this.timings[this.total_time_key] = datetime.datetime.now() - this.timings[this.total_time_key]

        logging.debug("Raw Timings:")
        logging.debug("------------")
        for key, value in this.timings.items():
            logging.debug(key + ": " + str(value) )

        header = "---------------------------------------"
        print(header)
        for name in this.timings:
            if not this.total_time_key in name:
                if not isinstance(this.timings[name], datetime.timedelta):
                    end_timing(name)
                duration = this.timings[name]
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                print( '{:29}'.format(name) + ": {:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds) )

        print(header)

        duration = this.timings[this.total_time_key]
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        print( '{:29}'.format(this.total_time_key) + ": {:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds) )

        print(header)

        this.timings_printed = True
