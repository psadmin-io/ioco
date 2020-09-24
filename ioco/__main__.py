<<<<<<< HEAD
"""psadmin.io cloud operations utility

usage:
    ioco dpk deploy [options]
                    [--setup-file-system]
                    [--install-packages]
                    [--get-dpk]
                    [--setup-dpk]
                    [--firewall-pia]
                    [--dpk-source=<type> --dpk-platform=<type> --dpk-type=<type>]
                    [--dpk-version=<nbr> --dpk-patch=<nbr>]
    ioco dpk undeploy [options]
    ioco oci block [options]
                   [--make-file-system]
                   [--mount]
                   [--block-path=<path>]
                   [--block-disk=<path>]
    ioco cm attach-dpk-files --nfs-host=<host>
                             --export=<export>
                             [options]                             
                             [--mount-path=<path>]
    ioco rundeck install [options]
    ioco example [options] [--example-path=<path>]

options:
    -h --help              Show this message and exit.
    -v --verbose           Show unnecessary extra information.
    -f --force             Forces a 'yes' answer to any prompts
    --home=<dir>           Working directory used by ioco.
                           default: '/u01/app/ioco'
    --conf=<file>          JSON config file
                           default: '[--home]/conf.json'
    --logs=<dir>           Directory for log files
                           default: '[--home]/logs'
    --cust-yaml=<file>     Location of psft_customizations.yaml
                           default: '[--home]/dpk/psft_customizations.yaml'
    --dpk-source=<type>    Use MOS or CM for dpk source
                           default: 'CM'
    --dpk-platform=<type>  DPK platform type
                           default: 'linux'
    --dpk-type=<type>      DPK application type
    --block-disk=<path>    OCI Block storage disk
                           default: '/dev/oracleoci/oraclevdb'
    --block-path=<path>    OCI Block storage mount path
                           default: '/u01/app/oracle/product'
    --mount-path=<path>    CM dpk files mount path
                           default: '/cm_psft_dpks'
"""
import os
import logging
import json
from docopt import docopt
from pathlib import Path

from ioco import dpk, util, oci, cm, rundeck, example

def main(): 
    # setup
    config = util.get_config(docopt(__doc__, version='0.1'))

    # generate examples
    if config['example']:
            example.main(config)
    else:
        util.setup_logging(config)
        logging.debug('config: \n' + json.dumps(config, indent=4, sort_keys=True))
        
        # timing setup
        util.init_timings()

        # ioco home setup
        util.setup_home(config)

        # dpk
        if config['dpk']:
            dpk.init(config)

            if config['deploy']:
                dpk.deploy()

            if config['undeploy']:
                dpk.undeploy()
        
        # oci
        if config['oci']:
            oci.main(config)
        
        # cm
        if config['cm']:
            if config['attach-dpk-files']:
                cm.attach(config)
                
        # rundeck
        if config['rundeck']:
            if config['install']:
                rundeck.install(config)

        util.print_timings()

if __name__ == '__main__':
    main()
=======
"""psadmin.io cloud operations utility

usage:
    ioco dpk deploy [options]
                    [--setup-file-system]
                    [--install-packages]
                    [--get-dpk]
                    [--setup-dpk]
                    [--firewall-pia]
                    [--dpk-source=<type> --dpk-platform=<type> --dpk-type=<type>]
                    [--dpk-version=<nbr> --dpk-patch=<nbr>]
    ioco dpk undeploy [options]
    ioco oci block [options]
                   [--make-file-system]
                   [--mount]
                   [--block-path=<path>]
                   [--block-disk=<path>]
    ioco cm attach-dpk-files [options]
                             [--nfs-host=<host>]
                             [--export=<export>]
                             [--mount-path=<path>]
    ioco vault read --secret-id=<secret-id>
                    [options]
    ioco rundeck install [options]
    ioco example [options] [--example-path=<path>]

options:
    -h --help              Show this message and exit.
    -v --verbose           Show unnecessary extra information.
    -f --force             Forces a 'yes' answer to any prompts
    -q --quiet             Hide timing formation
    --home=<dir>           Working directory used by ioco.
                           default: '/u01/app/ioco'
    --conf=<file>          JSON config file
                           default: '[--home]/conf.json'
    --logs=<dir>           Directory for log files
                           default: '[--home]/logs'
    --cust-yaml=<file>     Location of psft_customizations.yaml
                           default: '[--home]/dpk/psft_customizations.yaml'
    --dpk-source=<type>    Use MOS or CM for dpk source
                           default: 'CM'
    --dpk-platform=<type>  DPK platform type
                           default: 'linux'
    --dpk-type=<type>      DPK application type
    --block-disk=<path>    OCI Block storage disk
                           default: '/dev/oracleoci/oraclevdb'
    --block-path=<path>    OCI Block storage mount path
                           default: '/u01/app/oracle/product'
    --mount-path=<path>    CM dpk files mount path
                           default: '/cm_psft_dpks'
"""
import os
import logging
import json
from docopt import docopt
from pathlib import Path

from ioco import dpk, util, oci, cm, vault, rundeck, example

def main(): 
    # setup
    config = util.get_config(docopt(__doc__, version='0.1'))

    # generate examples
    if config['example']:
            example.main(config)
    else:
        # ioco home setup
        util.setup_home(config)
        
        util.setup_logging(config)
        logging.debug('config: \n' + json.dumps(config, indent=4, sort_keys=True))
        
        # timing setup
        util.init_timings()

        # dpk
        if config['dpk']:
            dpk.init(config)

            if config['deploy']:
                dpk.deploy()

            if config['undeploy']:
                dpk.undeploy()
        
        # oci
        if config['oci']:
            oci.main(config)
        
        # cm
        if config['cm']:
            if config['attach-dpk-files']:
                cm.attach(config)

        # vault
        if config['vault']:
            vault.init(config)
            
            if config['read']:
                vault.read_secret_value(config)
                
        # rundeck
        if config['rundeck']:
            if config['install']:
                rundeck.install(config)

        util.print_timings()

if __name__ == '__main__':
    main()
>>>>>>> 9301974fb1ec0a5352f6edb5a3400d9eb4ee392f
