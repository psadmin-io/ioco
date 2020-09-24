

variable compartment_id {
    description = "Network compartment ID"    
}

variable network_name {
    description = "Network prefix name"    
} 

variable enable_ig {
    description = "Enable Internet Gateway"
    default     = false
}

variable enable_ng {
    description = "Enable NAT Gateway"
    default     = false
}

variable enable_drg {
    description = "Enable Dynamic Routing Gateway"
    default     = false
}

variable vcn_cidr {
    description = "CIDR for VCN"
    default     = false
}   

variable sn_dmz_cidr {
    description = "CIDR for dmz subnet"
    default     = false
}    

variable sn_mgmt_cidr {
    description = "CIDR for mgmt subnet"
    default     = false
}    
variable sn_app_cidr {
    description = "CIDR for app subnet"
    default     = false
}    
variable sn_db_cidr {
    description = "CIDR for db subnet"
    default     = false
}    
variable sn_all_cidr {
    description = "CIDR for all subnet"
    default     = false
}    

variable cpe_ip_address {
    description = "CPE IP Address"
    default     = false
}

variable vpn_route_cidr {
    description = "Static Route CIDR for VPN Connection"
    default     = false
}
