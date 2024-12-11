output "application_insights_id" {
  value = { for k, v in module.app_insights_audit : k => v.id }
}

output "audit_networking_rg_name" {
  value = { for k, v in azurerm_resource_group.rg_vnet : k => v.name }
}

output "log_analytics_workspace_id" {
  value = { for k, v in module.log_analytics_workspace_audit : k => v.id }
}

output "private_endpoint_rg_name" {
  value = var.features.private_endpoints_enabled ? { for k,v in azurerm_resource_group.rg_private_endpoints : k => v.name } : {}
}

output "subnet_pep_id" {
  value = { for k, v in module.subnets : local.subnets_map[k].vnet_key => v.id if k == "${module.regions_config[local.subnets_map[k].vnet_key].names.subnet}-pep" }
}
