import os
import logging
import subprocess
from pathlib import Path
from ioco import util

def attach(config):
    timing_key = "cm attach-dpk-files"
    util.start_timing(timing_key)

    logging.debug("Attaching Cloud Manager DPK files repository")

    try:
        cm_nfs_host = config.get("--nfs-host")
        cm_export = config.get("--export")
        cm_mount_path = config.get("--mount-path")
    except KeyError as e:
        logging.error("INVALID config - Missing " + str(e) + " setting.")
        util.error_timings(timing_key)

    try:
        # mkdir
        Path(cm_mount_path).mkdir(parents=True, exist_ok=True)
    except:
        logging.error('Issue creating mount path directory')
        util.error_timings(timing_key)

    # if mount path directory is empty, assume it needs mounting
    if os.listdir(cm_mount_path) == []: 
        try:
            # mount
            cmd = [cm_nfs_host + ":" + cm_export, cm_mount_path]
            logging.debug(cmd)
            subprocess.run(["sudo","mount","-t","nfs"] + cmd, check=True)
            #, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)
            logging.debug('Mount successful')
        except:
            logging.error('Issue mounting path')
            util.error_timings(timing_key)
            raise
    else:
        logging.debug("Mount path already contains files, skip mounting")

    util.end_timing(timing_key)
