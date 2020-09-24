# provider "oci" {    
# }

# VCN

resource "oci_core_vcn" "vcn" {
    #count          = var.vcn_cidr==false ? 0 : 1  
    provider       = oci
    compartment_id = var.compartment_id
    cidr_block     = var.vcn_cidr
    display_name   = var.network_name
    dns_label      = var.network_name
}

# Gateways

resource "oci_core_internet_gateway" "ig" {
    count          = var.enable_ig==true ? 1 : 0
    provider       = oci
    compartment_id = var.compartment_id
    display_name   = "${var.network_name}-ig"
    vcn_id         = oci_core_vcn.vcn.id
}

resource "oci_core_nat_gateway" "ng" {
    count          = var.enable_ng==true ? 1 : 0
    provider       = oci
    compartment_id = var.compartment_id
    display_name   = "${var.network_name}-ng"
    vcn_id         = oci_core_vcn.vcn.id
}

resource "oci_core_drg" "drg" {
    count          = var.enable_drg==true ? 1 : 0
    provider       = oci
    compartment_id = var.compartment_id
    display_name   = "${var.network_name}-drg"
}

# Routes

resource "oci_core_route_table" "rt_ig" {
    count          = var.enable_ig==true ? 1 : 0
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "Internet Gateway Routes"
    route_rules {
        destination_type = "CIDR_BLOCK"
        destination = "0.0.0.0/0"
        network_entity_id = oci_core_internet_gateway.ig[count.index].id        
    }
}

resource "oci_core_route_table" "rt_ng" {
    count          = var.enable_ng==true ? 1 : 0
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "NAT Gateway Routes"
    route_rules {
        destination_type = "CIDR_BLOCK"
        destination = "0.0.0.0/0"
        network_entity_id = oci_core_nat_gateway.ng[count.index].id
    }
}

# VPN and CPE

resource "oci_core_cpe" "cpe" {
    count          = var.cpe_ip_address==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id    
    ip_address     = var.cpe_ip_address
    display_name = "${var.network_name}-cpe"
#   cpe_device_shape_id = "${data.oci_core_cpe_device_shapes.test_cpe_device_shapes.cpe_device_shapes.0.cpe_device_shape_id}"
}

resource "oci_core_ipsec" "vpn" {
    count          = var.cpe_ip_address==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id    
    cpe_id         = oci_core_cpe.cpe[count.index].id
    drg_id         = oci_core_drg.drg[count.index].id
    static_routes  = [var.vpn_route_cidr]
    display_name   = "${var.network_name}-vpn"
    #cpe_local_identifier = "${var.ip_sec_connection_cpe_local_identifier}"
    #cpe_local_identifier_type = "${var.ip_sec_connection_cpe_local_identifier_type}"
}

# Subnets

resource "oci_core_subnet" "sn_dmz" {
    count          = var.sn_dmz_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    
    display_name    = "dmz"
    dns_label       = "dmz"
    cidr_block      = var.sn_dmz_cidr
    route_table_id  = oci_core_route_table.rt_ig[count.index].id # TODO - how to handle route tables?
    dhcp_options_id = oci_core_vcn.vcn.default_dhcp_options_id
    #prohibit_public_ip_on_vnic = false TODO
    security_list_ids = [oci_core_vcn.vcn.default_security_list_id, oci_core_security_list.dmz[count.index].id]
}

resource "oci_core_subnet" "sn_all" {
    count          = var.sn_all_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    
    display_name    = "all"
    dns_label       = "all"
    cidr_block      = var.sn_all_cidr
    route_table_id  = oci_core_route_table.rt_ig[count.index].id # TODO - how to handle route tables?
    dhcp_options_id = oci_core_vcn.vcn.default_dhcp_options_id
    #prohibit_public_ip_on_vnic = false TODO
    #security_list_ids = [oci_core_vcn.vcn.default_security_list_id, oci_core_security_list.all[count.index].id]
}

resource "oci_core_subnet" "sn_mgmt" {
    count          = var.sn_mgmt_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    
    display_name    = "mgmt"
    dns_label       = "mgmt"
    cidr_block      = var.sn_mgmt_cidr
    route_table_id  = oci_core_route_table.rt_ig[count.index].id # TODO - how to handle route tables?
    dhcp_options_id = oci_core_vcn.vcn.default_dhcp_options_id
    #prohibit_public_ip_on_vnic = false TODO
    security_list_ids = [oci_core_vcn.vcn.default_security_list_id, oci_core_security_list.mgmt[count.index].id]
}

resource "oci_core_subnet" "sn_app" {
    count          = var.sn_app_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    
    display_name    = "app"
    dns_label       = "app"
    cidr_block      = var.sn_app_cidr
    route_table_id  = oci_core_route_table.rt_ig[count.index].id # TODO - how to handle route tables?
    dhcp_options_id = oci_core_vcn.vcn.default_dhcp_options_id
    #prohibit_public_ip_on_vnic = false TODO
    security_list_ids = [oci_core_vcn.vcn.default_security_list_id, oci_core_security_list.app[count.index].id]
}

resource "oci_core_subnet" "sn_db" {
    count          = var.sn_db_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    
    display_name    = "db"
    dns_label       = "db"
    cidr_block      = var.sn_db_cidr
    route_table_id  = oci_core_route_table.rt_ig[count.index].id # TODO - how to handle route tables?
    dhcp_options_id = oci_core_vcn.vcn.default_dhcp_options_id
    #prohibit_public_ip_on_vnic = false TODO
    security_list_ids = [oci_core_vcn.vcn.default_security_list_id, oci_core_security_list.db[count.index].id]
}

# Security Lists
# https://www.oracle.com/webfolder/technetwork/tutorials/obe/cloud/compute-iaas/plan_vcn_psft_cm_oci/index.html

resource "oci_core_security_list" "mgmt" {
    count          = var.sn_mgmt_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "mgmt Secruity List"
	
    # outbound
    egress_security_rules {
        protocol    = "6" # tcp
        destination = "0.0.0.0/0"
    }

    # inbound
    # mgmt
    ingress_security_rules {
        description = "FSS mount target - mgmt"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - mgmt"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "111"
            max = "111"  
        }
    }
    ingress_security_rules {
        description = "FSS mount target - mgmt"    
        protocol  = "17" # udp
        source    = var.sn_mgmt_cidr
        stateless = false   

        udp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - mgmt"    
        protocol  = "17" # udp
        source    = var.sn_mgmt_cidr
        stateless = false   

        udp_options {
            min = "111"  
            max = "111"  
        }
    }
    # app
    ingress_security_rules {
        description = "FSS mount target - app"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - app"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "111"  
            max = "111"  
        }
    }
    ingress_security_rules {
        description = "FSS mount target - app"    
        protocol  = "17" # udp
        source    = var.sn_app_cidr
        stateless = false   

        udp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - app"    
        protocol  = "17" # udp
        source    = var.sn_app_cidr
        stateless = false   

        udp_options {
            min = "111"  
            max = "111"  
        }
    }
    # db
    ingress_security_rules {
        description = "FSS mount target - db"    
        protocol  = "6" # tcp
        source    = var.sn_db_cidr
        stateless = false   

        tcp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - db"    
        protocol  = "6" # tcp
        source    = var.sn_db_cidr
        stateless = false   

        tcp_options {
            min = "111"  
            max = "111"  
        }
    }
    ingress_security_rules {
        description = "FSS mount target - db"    
        protocol  = "17" # udp
        source    = var.sn_db_cidr
        stateless = false   

        udp_options {
            min = "2048"  
            max = "2050"
        }
    }
    ingress_security_rules {
        description = "FSS mount target - db"    
        protocol  = "17" # udp
        source    = var.sn_db_cidr
        stateless = false   

        udp_options {
            min = "111"  
            max = "111"  
        }
    }
    # all    TODO
    ingress_security_rules {
        description = "PIA HTTP"    
        protocol  = "6" # tcp
        source    = "0.0.0.0/0"
        stateless = false   

        tcp_options {
            min = "8000"
            max = "8000"  
        }
    }
    ingress_security_rules {
        description = "PIA HTTPS"    
        protocol  = "6" # tcp
        source    = "0.0.0.0/0"
        stateless = false   

        tcp_options {
            min = "8443"
            max = "8443"  
        }
    }
}

resource "oci_core_security_list" "app" {
    count          = var.sn_app_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "app Secruity List"
	
    # outbound
    egress_security_rules {
        protocol    = "6" # tcp
        destination = "0.0.0.0/0"
    }

    # inbound
    # mgmt
    ingress_security_rules {
        description = "SSH"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "22"  
            max = "22"
        }
    }
    ingress_security_rules {
        description = "Winrm"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "5985"  
            max = "5986"
        }
    }
    ingress_security_rules {
        description = "CIFS"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "139"
            max = "139"  
        }
    }
    ingress_security_rules {
        description = "CIFS"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {  
            min = "445"
            max = "445"
        }
    }
    ingress_security_rules {
        description = "CIFS"    
        protocol  = "17" # UDP
        source    = var.sn_mgmt_cidr
        stateless = false   

        udp_options {
            min = "137"  
            max = "138"
        }
    }
    ingress_security_rules {
        description = "RDP - mgmt"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "3389"
            max = "3389"  
        }
    }
    # app
    ingress_security_rules {
        description = "PIA HTTP"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "8000"
            max = "8000"  
        }
    }
    ingress_security_rules {
        description = "PIA HTTPS"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "8443"
            max = "8443"  
        }
    }
    ingress_security_rules {
        description = "Elasticsearch"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "9200"
            max = "9200"  
        }
    }
    ingress_security_rules {
        description = "RDP - app"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "3389"  
            max = "3389"
        }
    }
}

resource "oci_core_security_list" "db" {
    count          = var.sn_db_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "db Secruity List"
	
    # outbound
    egress_security_rules {
        protocol    = "6" # tcp
        destination = "0.0.0.0/0"
    }

    # inbound
    # mgmt
    ingress_security_rules {
        description = "SSH"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "22"  
            max = "22"
        }
    }
    ingress_security_rules {
        description = "DB"    
        protocol  = "6" # tcp
        source    = var.sn_mgmt_cidr
        stateless = false   

        tcp_options {
            min = "1521"  
            max = "1522"
        }
    }
    # app
    ingress_security_rules {
        description = "DB"    
        protocol  = "6" # tcp
        source    = var.sn_app_cidr
        stateless = false   

        tcp_options {
            min = "1521"  
            max = "1522"
        }
    }
}
resource "oci_core_security_list" "dmz" {
    count          = var.sn_dmz_cidr==false ? 0 : 1
    provider       = oci
    compartment_id = var.compartment_id
    vcn_id         = oci_core_vcn.vcn.id
    display_name   = "dmz Secruity List"
	
    # outbound
    egress_security_rules {
        protocol    = "6" # tcp
        destination = "0.0.0.0/0"
    }

    # inbound
    ingress_security_rules {
        description = "SSH"    
        protocol  = "6" # tcp
        source    = "0.0.0.0/0"
        stateless = false   

        tcp_options {
            min = "22"  
            max = "22"
        }
    }
}