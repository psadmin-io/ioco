import logging
import subprocess
import shutil
from pathlib import Path
from ioco import util

def install(config):
    timing_key = "rundeck install"
    util.start_timing(timing_key)

    try:
        logging.debug("Setting up for install")
        rd_base = "/u01/app/rundeck" # TODO - assume this location?
        Path(rd_base).mkdir(parents=True, exist_ok=True)
        shutil.chown(rd_base, user="opc", group="opc") # TODO - assuming opc?
        
        logging.debug("Adding rundeck rpm")
        subprocess.run(["sudo","rpm", "-Uvh","https://repo.rundeck.org/latest.rpm"])

        logging.debug("Installing java and rundeck")
        subprocess.run(["sudo","yum", "-y", "install", "java-1.8.0", "rundeck"])

        logging.debug("Starting rundeck service")
        subprocess.run(["sudo","service", "rundeckd", "start"])

        logging.debug("Open firewall")
        subprocess.run(["sudo","firewall-cmd", "--zone=public", "--add-port=4440/tcp"], check=True)
    except:
        logging.error("Error setting up Rundeck")
        util.error_timings(timing_key)

    util.end_timing(timing_key)
