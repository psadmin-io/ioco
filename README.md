# ioCloudOps
```
psadmin.io cloud operations utility

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
                             [--persist-cm-mount]
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
```

# install 
## using pip
We have NOT published this to `pip` yet, but you can still install locally from the repo.
```
$ git clone https://github.com/psadmin-io/ioco.git
$ sudo python3 -m pip install ./ioco
$ ioco --help
$ sudo /usr/local/bin/ioco --help
```

## using python directly
```
# Manually install dependencies 
$ sudo python3 -m pip install docopt requests
$ git clone https://github.com/psadmin-io/ioco.git
$ cd ioco
$ sudo python3 -m ioco --help
```

# full example
```
sudo ioco oci block --make-file-system --mount
sudo ioco cm attach-dpk-files --nfs-host=$IOCO_NFS_HOST --export=$IOCO_CM_DPK_EXPORT
sudo ioco dpk deploy --dpk-source=CM --dpk-type=IH
```

# configuration

Configuration and command options can be set in multiple ways.

## hierarchy

1. Environment Variables
1. Command Line Arguments
1. JSON Configuration File

## environment variables

* IOCO_HOME
* IOCO_CONF
* IOCO_LOGS
* IOCO_YAML
* IOCO_VERBOSE
* MOS_USERNAME
* MOS_PASSWORD
