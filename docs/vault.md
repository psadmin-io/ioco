# Vault Operations

The `ioco vault` commands let you create, update, retrieve secrets from an OCI Vault.

## Prerequisites

Before using the `ioco vault` operations, you must configure OCI to allow Instance Principal authentication, and create and allow access to a Vault.

1. Create a new Dynamic Group for instances in your compartment
1. Create a new Vault and Master Key
1. Create a policy to allow the Dynamic Group to `manage secret-family` for your compartment

## Using the Vault Actions

*Read a Secret*

`oci vault read --secret-id <secret ocid>`

*Create New Secrets*

`oci vault create --field-name <field_name> --description '<Description>' --secret-value <secret_value>`

*Update a Secret*

`oci vault update --secret-id <secret ocid> --secret-value <secret_value>`

*Retrieve Passwords for YAML*

`oci vault yaml update`

`ioco` will look for secret OCID values in your `psft_customizations.yaml` file, retrieve the secret values from the Vault, and update the file with the secret value.

*Encrypt Passwords for YAML*

`oci vault yaml encrypt`

`ioco` will generate EYAML keys on the server and encrypt the passwords in your `psft_customizations.yaml` file.

