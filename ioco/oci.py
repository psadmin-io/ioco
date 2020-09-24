import os
import sys
import logging
import subprocess
from pathlib import Path
from ioco import util

this = sys.modules[__name__]
this.part = None
this.fs_type = None
this.config = None

def main(config):
    this.config = config
    if this.config.get("block"):
        timing_key = "oci block"
        util.start_timing(timing_key)

        logging.debug("Processing block command")
        this.part = this.config.get("--block-disk") + "1"
        this.fs_type = "xfs"

        # If no specific oci block options are set, then set all
        all = not this.config['--make-file-system'] \
            and not this.config['--mount'] 
        
        if all or this.config.get('--make-file-system'):
            make_file_system()
        if all or this.config.get('--mount'):
<<<<<<< HEAD
            mount_file_system

=======
            mount_file_system()
>>>>>>> 9301974fb1ec0a5352f6edb5a3400d9eb4ee392f
        util.end_timing(timing_key)

def make_file_system():
    logging.debug("Making file system for block volume")
    timing_key = "oci block make_file_system"
    util.start_timing(timing_key)

    # Create partition, if needed
    if os.path.exists(this.part):
        logging.debug("Partition on " + this.config.get("--block-disk") + " is already created")        
    else:
        logging.debug("Creating partition on " + this.config.get("--block-disk"))        
        try:
            fdisk_tmp_sh = config.get("--home") + "/ioco-oci-block-partition.sh"
            f = open(fdisk_tmp_sh,"w")
            f.write("sudo fdisk " + this.config.get("--block-disk") + " <<EOF\nn\np\n\n\n\nw\nEOF")
            f.close()
        except:
            logging.error("Issue creating temp partition setup script")
            util.error_timings(timing_key)

        try:    
            subprocess.run(["sudo","sh", fdisk_tmp_sh], check=True)
        except:
            logging.error("Issue creating partion")
            util.error_timings(timing_key)

    # Create file system, if needed
    logging.debug("Creating file sytem using " + this.part)        
    try:
        subprocess.run(["sudo","mkfs." + this.fs_type, this.part], check=True)
    except:
        logging.info("File system did NOT create, assuming already created")
        util.error_timings(timing_key)
    
    util.end_timing(timing_key)


def mount_file_system():
    logging.debug("Mounting")
    timing_key = "oci block mount"
    util.start_timing(timing_key)

    try:
<<<<<<< HEAD
        Path(config.get('--mount-path')).mkdir(parents=True, exist_ok=True)
=======
        Path(config.get('--block-path')).mkdir(parents=True, exist_ok=True)
>>>>>>> 9301974fb1ec0a5352f6edb5a3400d9eb4ee392f
        
        mount_tmp_sh = config.get("--home") + "/ioco-oci-block-mount.sh"
        f = open(mount_tmp_sh,"w")
        f.write("#!/bin/bash\n")
        f.write("if ! grep -q '" + part + "' /etc/fstab ; then\n")
        f.write("    echo '# ioco-oci-block-mount' >> /etc/fstab\n")
        f.write("    echo '" + part + " " + config.get("--block-path") + " " + fs_type + " defaults 0 2' >> /etc/fstab\n")
        f.write("fi")
        f.close()
        
        subprocess.run(["sudo","sh", mount_tmp_sh], check=True)
        subprocess.run(["sudo","mount", "-a"], check=True)
    except:
        logging.error("Issue mounting partion")
        util.error_timings(timing_key)
        raise

<<<<<<< HEAD
    util.end_timing(timing_key)
=======
    util.end_timing(timing_key)
>>>>>>> 9301974fb1ec0a5352f6edb5a3400d9eb4ee392f
