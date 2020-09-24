variable "tenancy_ocid" {
    description = "OCI tenancy ID"
    default     = "ocid1.tenancy.oc1..aaaaaaaanyfpnxnvo2yz2zkmqoymvmjvenua7pzmjxwjvsihdh6d3v4ul7sa"
    # TODO
}
variable "region_old" {
    description = "Region for on-prem data center (old)"
    default     = "ca-toronto-1"
    # TODO
}
variable "region_new" {
    description = "Region for OCI (new)"
    default     = "us-ashburn-1"
    # TODO
}
# variable "region_new_dr" {
#     description = ""
#     default     = "us-phoenix-1"
# }
variable compartment_id {
    description = "Parent compartment ID"
    default     = "ocid1.compartment.oc1..aaaaaaaar5slanr5lwntp6zx4wgnk7isx2cckri7tq3w7qfdyh3w4vk5o6lq"
    # TODO
}

variable ssh_public_key {
    description = "SSH Public Key"
    default = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGxS5UbtOmgAn61FHmd75mH+ZyDrUxq8ThTNTzsQfT1wEAW1lbSbAmQse5p3LrsyaTdXxiK/sNjt6pYv7j6HCXTKunJV0NAnXa0qLduFkDd396z/cMVI/jdGT6M4/tAsrtkTUvHyCw+EGQKFCLxNcCARZqATY3nP/Emb6NxGmFrJQYSdsrAzeTAeNCoBH1bR3DlK54v8kvKVsJ6FgZEq4HoXxom1toph613Ylpp7NzQkN6pYwFEloCQ0GT0hsaBSwB3O0Gz+PuXXDekwJeG0y3vfwiQxKUxOLnZNczQ/zfgUdMr1q04s2XSkcM7vyMlOBO9wAoCchvE2uRRmCPtvw9"
    # TODO
}

variable ad_old {
    description = "old Region Availability Domain"
    default     = "zYxB:CA-TORONTO-1-AD-1"
}

variable image_lnx {
    description = "Linux Image OCID"
    default = "ocid1.image.oc1.ca-toronto-1.aaaaaaaaemkdkubr2znyndgbrhmgn4e2quojqu3maurpf2whxqp3p7bl5spq"
}