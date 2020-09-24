provider "oci" {
  alias  	   = "old"
  tenancy_ocid = var.tenancy_ocid
  region       = var.region_old  
}

provider "oci" {
  alias  	   = "new"
  tenancy_ocid = var.tenancy_ocid
  region       = var.region_new
}

# provider "oci" {
#   alias  	   = "new-dr"
#   tenancy_ocid = var.tenancy_ocid
#   region       = var.region_iooci-dr
# }

# OCI DR
# TODO - network

# OCI Production (new)

module "network-new" {
	source = "./modules/network"

    compartment_id = var.compartment_id
	network_name   = "new"
	enable_ig      = true
	enable_drg     = true
	vcn_cidr       = "10.10.0.0/16"
	sn_dmz_cidr    = "10.10.0.0/24"
	sn_mgmt_cidr   = "10.10.1.0/24"
	sn_app_cidr    = "10.10.2.0/24"
	sn_db_cidr     = "10.10.3.0/24"
	# sn_all_cidr  = false
	cpe_ip_address = false # "140.238.158.197" # libreswan VM public IP
    vpn_route_cidr = false # "192.168.0.0/16" # TODO same as VCN Old CIDR
	providers = { 
		oci = oci.new
	}
}

# "On-Prem" Datacenter (old)

module "network-old" { 
	source = "./modules/network"

    compartment_id = var.compartment_id
	network_name   = "old"
	enable_ig      = true
	vcn_cidr       = "192.168.0.0/16"
	sn_dmz_cidr    = "192.168.0.0/24"
	# sn_mgmt_cidr = false
	# sn_app_cidr  = false
	# sn_db_cidr   = false
	sn_all_cidr    = "192.168.1.0/24"

	providers = { 
		oci = oci.old
	}
}

# VPN VM
resource "oci_core_instance" "inst_vpn" {  
	provider            = oci.old
	compartment_id      = var.compartment_id
	availability_domain = var.ad_old
	display_name        = "cpevpn"
	shape               = "VM.Standard2.1"

    source_details {
        source_id       = var.image_lnx
        source_type     = "image"
    }

    create_vnic_details {                
        hostname_label   = "cpevpn"
        subnet_id        = module.network-old.sn_dmz_id
    }    

    metadata = {                      
        ssh_authorized_keys = var.ssh_public_key
    }    
      
    timeouts {
        create = "120m"
    }
}

# PSFT test
resource "oci_core_instance" "inst_psftold" {  
	provider            = oci.old
	compartment_id      = var.compartment_id
	availability_domain = var.ad_old
	display_name        = "psftold"
	shape               = "VM.Standard2.1"

    source_details {
        source_id       = var.image_lnx
        source_type     = "image"
    }

    create_vnic_details {                
        hostname_label   = "psftold"
        subnet_id        = module.network-old.sn_dmz_id
    }    

    metadata = {                     
        ssh_authorized_keys = var.ssh_public_key
    }    
      
    timeouts {
        create = "120m"
    }
}

resource "oci_core_volume" "vol_psftold" {  
	provider            = oci.old
	compartment_id      = var.compartment_id
	availability_domain = var.ad_old 
    display_name        = "psftold"
    size_in_gbs         = "200"
    # vpus_per_gb         = var.volume_perf

    # source_details {
    #     #backup id goes here TODO - shuffle on app
    #     id = var.volume_id
    #     type = var.volume_type
    # }     
}

resource "oci_core_volume_attachment" "vol_attach" { 
	provider            = oci.old
    depends_on      = [oci_core_volume.vol_psftold, oci_core_instance.inst_psftold]
    display_name    = "psft"
    attachment_type = "paravirtualized"
    instance_id     = oci_core_instance.inst_psftold.id
    volume_id       = oci_core_volume.vol_psftold.id
}