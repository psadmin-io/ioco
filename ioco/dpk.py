import os
import sys
import logging
import subprocess
import requests
import ssl
import json
import re
import shutil
import zipfile
from http.cookiejar import MozillaCookieJar
from multiprocessing.pool import ThreadPool
from requests.auth import HTTPBasicAuth
from pathlib import Path
from ioco import util

# Module Variables
this = sys.modules[__name__]
this.config = None

def init(config):
    # TODO - move this to some setup method
    this.config = config
    
    # validate the config  
    try:
        # json config
        this.config['patch_id']
        this.config['download_threads']
        this.config['psft_base_dir']
        this.config['user_home_dir'] 
        this.config['ps_cfg_dir']
        this.config['pia_port']
        this.config['cm_dpk_files_dir']
    except KeyError as e:
        logging.error("INVALID config - Missing " + str(e) + " setting in json config.")
        sys.exit(1)
    except :
        logging.error("Config is not valid due to unknown exception.")
        sys.exit(99) # unknown
    
    try:
        # args
        this.config['--setup-file-system'] 
        this.config['--install-packages'] 
        this.config['--get-dpk'] 
        this.config['--setup-dpk']
        this.config['--dpk-source']
        this.config['--dpk-platform']
        this.config['--dpk-type']
        this.config['--persist-cm-mount']
    except KeyError as e:
        logging.error("INVALID arguments - Missing " + str(e) + " in arguments.")
        sys.exit(1)
    except :
        logging.error("Config is not valid due to unknown exception.")
        sys.exit(99) # unknown

    try:
        # environtment variables
        # TODO - move this to some setup method
        if this.config['--dpk-source'] == 'MOS':
            os.environ["MOS_USERNAME"]
            os.environ["MOS_PASSWORD"]
    except KeyError as e:
        logging.error("INVALID variables - Environment variables " + str(e) + " needs to be set.")
        sys.exit(1)
    except :
        logging.error("Config is not valid due to unknown exception.")
        sys.exit(99) # unknown

    # If no specific dpk phases are set, then set all
    this.config['--all-dpk'] = not this.config['--setup-file-system'] \
        and not this.config['--install-packages'] \
        and not this.config['--get-dpk'] \
        and not this.config['--setup-dpk'] \
        and not this.config['--firewall-pia']

    # Setting credential variables
    this.config['mos_username']  = os.getenv("MOS_USERNAME")
    this.config['mos_password']  = os.getenv("MOS_PASSWORD")
    
    # Setting other config
    this.config['dpk_status_file'] = this.config.get('dpk_files_dir') + '/dpk_status.json'

def deploy():
    timing_key = "dpk deploy"
    util.start_timing(timing_key)
    __banner()
    
    if this.config.get('--all-dpk') or this.config.get('--setup-file-system'):
        __setup_file_system()
    if this.config.get('--all-dpk') or this.config.get('--install-packages'):
        __install_packages()
    if this.config.get('--all-dpk') or this.config.get('--get-dpk'):
        __get_dpk()
    if this.config.get('--all-dpk') or this.config.get('--setup-dpk'):
        __setup_dpk()
    if this.config.get('--all-dpk') or this.config.get('--firewall-pia'):
        __firewall_pia()

    __done()

    util.end_timing(timing_key)
   
def undeploy():
    # TODO - Issue #3 convert this to more python based, not just bash in sub-process
    timing_key = "dpk undeploy"
    util.start_timing(timing_key)
    try:
        subprocess.run(['sudo','pkill', '-9', '-u', 'psadm2'], \
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run(['sudo','pkill', '-9', '-u', 'oracle2'], \
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run(['sudo','rm','-rf',this.config.get('psft_base_dir')], \
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run(['sudo','rm','-rf','/opt/oracle/psft/db/oraInventory'], \
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run(['sudo','rm','-f','/etc/oraInst.loc'], \
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logging.info('Done undeploying. An instance reboot may be required before next deploy.')
    except:
        logging.error('Issue undeploying')
        util.error_timings(timing_key)
        raise

    util.end_timing(timing_key)

def update_dpk_status(step, status):
    try:
        with open(this.config.get('dpk_status_file'), 'r+') as f:
            dpk_status = json.load(f)
            dpk_status[step] = status
            f.seek(0)
            f.truncate()
            json.dump(dpk_status, f)
    except:
        logging.error('Issue updating dpk status json file')

def __banner():
    logging.info("")
    logging.info(".:. ioCloudOps . dpk .:.")
    logging.info("")

def __setup_file_system():
    logging.info("Setting up file system")

    try:
        Path(this.config.get('dpk_files_dir')).mkdir(parents=True, exist_ok=True)
        logging.debug("Created DPK files directory: " + this.config.get('dpk_files_dir'))
        Path(this.config.get('psft_base_dir')).mkdir(parents=True, exist_ok=True)
        logging.debug("Created base directory: " + this.config.get('psft_base_dir'))
        Path(this.config.get('dpk_deploy_dir')).mkdir(parents=True, exist_ok=True)
        logging.debug("Created dpk directory: " + this.config.get('dpk_deploy_dir'))
        Path(this.config.get('user_home_dir')).mkdir(parents=True, exist_ok=True)
        logging.debug("Created home directory: " + this.config.get('user_home_dir'))
        os.umask(0)
        Path(this.config.get('ps_cfg_dir')).mkdir(mode=0o777, parents=True, exist_ok=True)
        logging.debug("Created PS_CFG_HOME directory: " + this.config.get('ps_cfg_dir'))
    except FileExistsError as e:
        logging.debug(e)
        pass
    except Exception as e:
        logging.error("There was an issue setting up the file system.")
        logging.error(e)

def __install_packages():
    logging.info("Installing packages")
    timing_key = "dpk deploy install_packages"
    util.start_timing(timing_key)
    try:
        packages = ["oracle-database-preinstall-19c", "glibc-devel"]
        subprocess.run(["sudo","yum", "-y", "install"] + packages, \
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logging.debug("Installing packages completed.")
    except:
        logging.error("Installing packages failed.")

    util.end_timing(timing_key)

def __get_dpk():
    logging.info("Getting DPK files")
    logging.debug("Determine DPK source method")

    # status
    __get_dpk_status()  

    # download or copy
    if this.config.get('downloaded_patch_files'):
        logging.info(" - Already got files")
    else:
        if this.config.get('--dpk-source') == "CM":
            __get_dpk_cm()
        else:
            __get_dpk_mos()

    # unpack
    __unpack_dpk()

def __get_dpk_cm():
    logging.info(" - Getting files from DPK repo")
    timing_key = "dpk deploy __get_dpk_cm"
    util.start_timing(timing_key)

    # Get dpk source dir
    try:
        repo = Path(this.config.get('cm_dpk_files_dir'))
        dpk_path = repo / 'dpk' / this.config.get('--dpk-platform') / this.config.get('--dpk-type')
        logging.debug("DPK type base: " + str(dpk_path))
    except TypeError:
        logging.error("Issue generating dpk path. Are --dpk-platform and --dpk-type set correctly?")
        exit(5)
    except:
        logging.error("Unknown issue generating dpk path")
        raise

    # Get DPK version
    if this.config.get('--dpk-version'):
        dpk_version = this.config.get('--dpk-version')
    else:
        # Get max DPK version 
        try:
            versions = [f.name for f in os.scandir(dpk_path) if f.is_dir() and f.name.isdigit()]
            logging.debug("DPK versions found: " + str(versions))
        except FileNotFoundError as e:
            logging.error(str(e) + ". Use CM to subscribe and download this type and platform.")
            util.error_timings(timing_key)
            exit(5)

        versions.sort(reverse=True)
        dpk_version = versions[0]

    dpk_path = dpk_path / dpk_version 
    logging.debug(this.config.get('--dpk-platform') + " " 
        + this.config.get('--dpk-type') + " DPK version found: " + str(dpk_version))
    
    if this.config.get('--dpk-type') == 'tools':        
        # Get DPK patch
        if this.config.get('--dpk-patch'):
            dpk_patch = this.config.get('--dpk-patch')
        else:
            # Get max DPK tools patch
            try:
                versions = [f.name for f in os.scandir(dpk_path) if f.is_dir() and f.name.isdigit()]
                logging.debug("DPK tools patches found: " + str(versions))
            except FileNotFoundError as e:
                logging.error(str(e) + ". Use CM to subscribe and download this type and platform.")
                util.end_timing(timing_key)
                util.print_timings()
                exit(5)
    
            versions.sort(reverse=True)
            dpk_patch = versions[0]
        
        dpk_path = dpk_path / dpk_patch 
        logging.debug(this.config.get('--dpk-platform') + " " 
            + "DPK tools patch found: " + str(dpk_patch))

    # copy dpk files
    try:
        logging.debug("Copying " + str(dpk_path) + " to " + this.config.get('dpk_files_dir')) 
        source_dpks = os.listdir(dpk_path)
        for f in source_dpks:
            full_f = os.path.join(dpk_path, f)
            if os.path.isfile(full_f): #TODO - only zip?
                shutil.copy(full_f, this.config.get('dpk_files_dir'))

        logging.debug("Update DPK status - downloaded_patch_files: true")
        update_dpk_status('downloaded_patch_files',True)

    except FileExistsError:
        logging.error("DPK files in working directory already exist")
        exit(2) 
    except:
        logging.error("Issue copying DPK files from source to tmp working directory")
        util.end_timing(timing_key)
        util.print_timings()
        raise

    util.end_timing(timing_key)

def __get_dpk_mos():
    logging.info(" - Downloading files from MOS")
    timing_key = "dpk deploy __get_dpk_mos"
    util.start_timing(timing_key)
    
    logging.debug("Creating auth cookie from MOS")
    cookie_file = this.config.get('dpk_files_dir') + "/mos.cookie"

    # eat any old cookies
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
        
    try:
        # Create a session and update headers
        s = requests.session()
        s.headers.update({'User-Agent': 'Mozilla/5.0'})

        # Initiate updates.oracle.com request to get login redirect URL
        logging.debug('Requesting downloads page')
        r = s.get("https://updates.oracle.com/Orion/Services/download", allow_redirects=False)
        login_url = r.headers['Location']
        if not login_url:
            logging.error("Location was empty so login URL can't be set") 
            util.error_timings(timing_key)
            exit(2)

        # Create a NEW session, then send Basic Auth to login redirect URL
        logging.debug('Sending Basic Auth to login, using new session')
        s = requests.session()
        logging.debug("Using MOS username: " + this.config.get('mos_username'))
        r = s.post(login_url, auth = HTTPBasicAuth(this.config.get('mos_username'), this.config.get('mos_password')))
            
        # Save session cookies to be used by downloader later on...
        this.config['mos_cookies'] = s.cookies

        # Validate login was success                 
        if r.ok:
            logging.debug("MOS login was successful")
        else:
            logging.error("MOS login was NOT successful.")
            util.error_timings(timing_key)
            exit(2)
    except:
        logging.error("Issue getting MOS auth token")
        util.end_timing(timing_key)
        raise

    try:
        # Use same session to search for downloads
        logging.debug('Search for list of downloads, using same session')
        mos_uri_search = "https://updates.oracle.com/Orion/SimpleSearch/process_form?search_type=patch&patch_number=" + this.config.get('patch_id') + "&plat_lang=226P"
        r = s.get(mos_uri_search) 
        search_results = r.content.decode('utf-8')
        
        # Validate search results                 
        if r.ok:
            logging.debug("Search results return success")
        else:
            logging.error("Search results did NOT return success")
            util.error_timings(timing_key)
            exit(2)
    except:
        logging.error("Issue getting MOS search results")
        util.end_timing(timing_key)
        raise
        
    try:        
        # Extract download links to list
        pattern = "https://.+?Download/process_form/[^\"]*.zip[^\"]*"
        download_links = re.findall(pattern,search_results)
        download_links_file = this.config.get('dpk_files_dir') + "/mos-download.links" 
        # Write download links to file
        f = open(download_links_file,"w")
        for link in download_links:
            # Write download links list to file
            logging.debug(link)
            f.write(link + os.linesep)
        f.close()

        # Validate download links
        if len(download_links) > 0:
            logging.info(" - Downloading " + str(len(download_links)) + " files")
        else:
            logging.error("No download links found")
            util.error_timings(timing_key)
            exit(2)
    except:
        logging.error("Issue creating download links file")
        util.end_timing(timing_key)
        raise

    # multi thread download
    results = ThreadPool(this.config.get('download_threads')).imap_unordered(__download_file, download_links)
    for r in results:
        logging.info("    [DONE] " + r)
    
    logging.debug("Update DPK status - downloaded_patch_files: true")
    update_dpk_status('downloaded_patch_files',True)
    util.end_timing(timing_key)

def __unpack_dpk():
    # Unpack setup scripts
    timing_key = "dpk deploy __unpack_dpk"
    util.start_timing(timing_key)
    if this.config.get('unpacked_setup_scripts'):
        logging.debug("DPK setup scripts are already unpacked")
    else:
        logging.debug("Unpacking DPK setup scripts")
            
        try:
            for p in Path(this.config.get('dpk_files_dir')).glob("*_1of*.zip"):
                with zipfile.ZipFile( p, 'r') as zip_ref:
                    zip_ref.extractall(this.config.get('dpk_files_dir'))
        except:
            logging.error("Issue unpacking setup scripts")
            util.error_timings(timing_key)
            exit(2)
        
        try:
            # Change permissions on setup folder
            for root, dirs, files in os.walk(this.config.get('dpk_files_dir') + "/setup"):  
                for momo in files:
                    os.chmod(os.path.join(root, momo), 775)
        except:
            logging.error("Issue setting permissions on unpacked setup scripts")
            util.error_timings(timing_key)
            raise
            exit(2)

        logging.debug("Update DPK status - unpacked_setup_scripts: true")
        update_dpk_status('unpacked_setup_scripts',True)
        
    util.end_timing(timing_key)

def __get_dpk_status():
    # Checking DPK download status
    if not os.path.exists(this.config.get('dpk_status_file')):
        logging.debug("DPK Status File missing - creating it now")
        try:
            with open(this.config.get('dpk_status_file'),'w') as f:
                dpk_status = {"downloaded_patch_files": False,"unpacked_setup_scripts": False}
                json.dump(dpk_status, f)
        except FileNotFoundError:
            logging.error("DPK files directory not created. Try again with '--setup-file-system'")
            util.error_timings(timing_key)
            exit(2)
        except:
            logging.error("Issue creating DPK status file")
            raise
    else:
        try:
            with open(this.config.get('dpk_status_file')) as f:
                dpk_status = json.load(f)
        except:
            logging.error("Issue opening DPK status file")

    logging.debug("DPK status: \n" + json.dumps(dpk_status))
    this.config['downloaded_patch_files'] = dpk_status['downloaded_patch_files']
    this.config['unpacked_setup_scripts'] = dpk_status['unpacked_setup_scripts']
    logging.debug("download_patch_files")
    
def __download_file(url):
    # assumes that the last segment after the / represents the file name
    # if url is abc/xyz/file.txt, the file name will be file.txt
    file_name_start_pos = url.rfind("=") + 1
    file_name = url[file_name_start_pos:]
    s = requests.session()
    s.cookies =  this.config.get('mos_cookies') 
    r = s.get(url, stream=True)
    if r.status_code == requests.codes.ok:
        with open(this.config.get('dpk_files_dir') + "/" + file_name, 'wb') as f: 
            for data in r:
                f.write(data)

    return file_name
    
def __setup_dpk():
    logging.info("Running DPK setup scripts")
    
    timing_key = "dpk deploy __setup_dpk"
    util.start_timing(timing_key)

    # generate_response_file
    logging.debug("Generating response file at " + this.config.get('dpk_files_dir') + "/response.cfg")
    try:
        rsp_file = open(this.config.get('dpk_files_dir') + "/response.cfg","w") 
        if this.config.get('--dpk-type') == 'tools':
            type_responses = [
                "env_type  = \"midtier\"\n",
                "db_platform = \"ORACLE\"\n"
            ]
        else:
            type_responses = [
                "env_type  = \"fulltier\"\n",
                "db_type = \"DEMO\"\n"
            ]

        responses = type_responses + [
            "psft_base_dir = \"" + this.config.get('psft_base_dir') + "\"\n",
            "dpk_location = \"" + this.config.get('dpk_deploy_dir') + "\"\n",
            "user_home_dir = \"" + this.config.get('user_home_dir') + "\"\n",
            "db_name = \"" + this.config.get('db_name') + "\"\n",
            "db_service_name = \"" + this.config.get('db_service_name') + "\"\n",
            "db_host = \"" + this.config.get('db_host') + "\"\n",
            "install_type = \"PUM\"\n",
            "admin_pwd = \"" + this.config.get('admin_pwd') + "\"\n",
            "connect_id = \"" + this.config.get('connect_id') + "\"\n",
            "connect_pwd = \"" + this.config.get('connect_pwd') + "\"\n",
            "access_pwd  = \"" + this.config.get('access_pwd') + "\"\n",
            "opr_id = \"" + this.config.get('opr_id') + "\"\n",
            "opr_pwd = \"" + this.config.get('opr_pwd') + "\"\n",
        # "domain_conn_pwd = \"P@ssw0rd_\"\n",
            "weblogic_admin_pwd  = \"" + this.config.get('weblogic_admin_pwd') + "\"\n",
            "webprofile_user_pwd = \"" + this.config.get('webprofile_user_pwd') + "\"\n",
            "gw_user_pwd = \"" + this.config.get('gw_user_pwd') + "\"\n",
            "gw_keystore_pwd = \"" + this.config.get('gw_keystore_pwd') + "\"\n",
        ]
        rsp_file.writelines(responses)
        rsp_file.close()
    except:
        logging.error('Issue generating response file')
        util.end_timing(timing_key)
        util.print_timings()
        raise
        exit(3)

    # generate psft_customizations.yaml file
    if os.path.exists(this.config.get('--cust-yaml')):
        logging.debug("psft_customizations.yaml file found at " + this.config.get('--cust-yaml'))
    else:
        logging.debug("Generating default psft_customizations.yaml file at " + this.config.get('--cust-yaml'))
        try:
            yaml_file = open(this.config.get('--cust-yaml'),"w") 
            yaml_lines = [
                    "---",
                    "\n# defaults generated by ioco",
                    "\ndpk_location:     " + this.config.get('dpk_deploy_dir'),
                    "\nuser_home_dir:    " + this.config.get('user_home_dir'),
                    "\nps_config_home:   " + this.config.get('ps_cfg_dir')
            ]
            yaml_file.writelines(yaml_lines)
            yaml_file.close()
        except:
            logging.error('Issue generating response file')
            util.error_timings(timing_key)
            raise
            exit(3)

    # execute_psft_dpk_setup
    logging.debug("Executing DPK Setup")

    if os.name == 'nt':
        logging.warning("Windows is not supported at this time.")
    else:
        setup_script = this.config.get('dpk_files_dir') + "/setup/psft-dpk-setup.sh"
        dpk_logfile = open(this.config.get('--logs') + "/psft-dpk-setup.log","w")
        try:
            subprocess.run(["sh", setup_script, 
                "--silent", 
                "--dpk_src_dir " + this.config.get('dpk_files_dir'), 
                "--response_file " + this.config.get('dpk_files_dir') + "/response.cfg", 
                "--customization_file " + this.config.get('--cust-yaml'),
#                    "--no_puppet_run"
            ], check=True, stdout=dpk_logfile, stderr=dpk_logfile)
        except:
            logging.error("DPK setup script failed.")
            util.error_timings(timing_key)
            raise
    util.end_timing(timing_key)
    
def __firewall_pia():
    logging.info("Updating firewall for PIA")
    try:
        subprocess.run(["sudo","firewall-cmd", "--zone=public", "--add-port=" + str(this.config.get('pia_port')) + "/tcp"], check=True)
    except:
        logging.error("Firewall PIA port failed.")
        raise

def __done():
    logging.info("")
    logging.info("DPK deployment is complete!")
