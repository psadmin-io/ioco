output "sn_dmz_id" {
    value = length(oci_core_subnet.sn_dmz) > 0 ? oci_core_subnet.sn_dmz[0].id : ""
}
output "sn_mgmt_id" {
    value = length(oci_core_subnet.sn_mgmt) > 0 ? oci_core_subnet.sn_mgmt[0].id : ""
}
output "sn_app_id" {
    value = length(oci_core_subnet.sn_app) > 0 ? oci_core_subnet.sn_app[0].id : ""
}
output "sn_db_id" {
    value = length(oci_core_subnet.sn_db) > 0 ? oci_core_subnet.sn_db[0].id : ""
}
output "sn_all_id" {
    value = length(oci_core_subnet.sn_all) > 0 ? oci_core_subnet.sn_all[0].id : ""
}