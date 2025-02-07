module "storage" {
  for_each = local.storage_accounts_map

  source = "../../../dtos-devops-templates/infrastructure/modules/storage"

  name                = substr("${module.regions_config[each.value.region].names.storage-account}${lower(each.value.name_suffix)}", 0, 24)
  resource_group_name = azurerm_resource_group.core[each.value.region].name
  location            = each.value.region

  containers = each.value.containers

  account_replication_type      = each.value.replication_type
  account_tier                  = each.value.account_tier
  public_network_access_enabled = each.value.public_network_access_enabled

  rbac_roles = local.rbac_roles_storage

  log_analytics_workspace_id                              = data.terraform_remote_state.audit.outputs.log_analytics_workspace_id[local.primary_region]
  monitor_diagnostic_setting_storage_account_enabled_logs = local.monitor_diagnostic_setting_storage_account_enabled_logs
  monitor_diagnostic_setting_storage_account_metrics      = local.monitor_diagnostic_setting_storage_account_metrics

  # Private Endpoint Configuration if enabled
  private_endpoint_properties = var.features.private_endpoints_enabled ? {
    private_dns_zone_ids_blob            = [data.terraform_remote_state.hub.outputs.private_dns_zones["${each.value.region}-storage_blob"].id]
    private_dns_zone_ids_queue           = [data.terraform_remote_state.hub.outputs.private_dns_zones["${each.value.region}-storage_queue"].id]
    private_endpoint_enabled             = var.features.private_endpoints_enabled
    private_endpoint_subnet_id           = module.subnets["${module.regions_config[each.value.region].names.subnet}-pep"].id
    private_endpoint_resource_group_name = azurerm_resource_group.rg_private_endpoints[each.value.region].name
    private_service_connection_is_manual = var.features.private_service_connection_is_manual
  } : null

  depends_on = [
    module.peering_spoke_hub,
    module.peering_hub_spoke
  ]

  tags = var.tags
}

locals {
  storage_accounts_flatlist = flatten([
    for region in keys(var.regions) : [
      for storage_key, storage_val in var.storage_accounts : {
        name                          = "${storage_key}-${region}"
        region                        = region
        name_suffix                   = storage_val.name_suffix
        replication_type              = storage_val.replication_type
        account_tier                  = storage_val.account_tier
        public_network_access_enabled = storage_val.public_network_access_enabled
        containers                    = storage_val.containers
      }
    ]
  ])

  # Project the above list into a map with unique keys for consumption in a for_each meta argument
  storage_accounts_map = { for storage in local.storage_accounts_flatlist : storage.name => storage }
}
