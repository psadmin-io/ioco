import logging
from ioco import util
import oci
import base64
import sys

# Module Variables
this = sys.modules[__name__]
this.config = None
this.signer = None
this.secret_client = None
this.vault_client = None

def init(config):
    # Get Instance Principal context
    this.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    this.secret_client = oci.secrets.SecretsClient(config={}, signer=this.signer)
    
def main(config):
    this.config = config

def read_secret_value(config):
    logging.debug("Reading secret from Vault")
    timing_key = "vault read"
    util.start_timing(timing_key)

    try:
        secret_id = config['--secret-id']
        response = this.secret_client.get_secret_bundle(secret_id)
    except:
        logging.error("Error reading from Vault")
        util.error_timings(timing_key)
        raise
    
    try:
        base64_secret_content = response.data.secret_bundle_content.content
        base64_secret_bytes = base64_secret_content.encode('ascii')
        base64_message_bytes = base64.b64decode(base64_secret_bytes)
        secret_content = base64_message_bytes.decode('ascii')
    except:
        logging.error("Error decoding secert")
        util.error_timings(timing_key)
        raise

    print("{}".format(secret_content))

# def create_secret(compartment_id, secret_content, secret_name, valult_id, key_id):
#     logging.debug("Creating a secret")
#     timing_key = "vault create"
#     util.start_timing(timing_key)
     
#     # Create secret_content_details that needs to be passed when creating secret.
#     secret_description = "This is just a test"
#     secret_content_details = oci.vault.models.Base64SecretContentDetails(content_type=oci.vault.models.SecretContentDetails.CONTENT_TYPE_BASE64,
#                                                                name=secret_content,
#                                                                stage="CURRENT",
#                                                                content=secret_content)
#     secrets_details = oci.vault.models.CreateSecretDetails(compartment_id=compartment_id,
#                                                            description = secret_description, 
#                                                        secret_content=secret_content_details,
#                                                        secret_name=secret_name,
#                                                        vault_id=vault_id,
#                                                        key_id=key_id)
 
#     #Create secret and wait for the secret to become active
#     response = this.vault_client_composite.create_secret_and_wait_for_state(create_secret_details=secrets_details,
#                                                                         wait_for_states=[
#                                                                     oci.vault.models.Secret.LIFECYCLE_STATE_ACTIVE])
#     util.end_timing(timing_key)
    
