module "postgresql_flexible_db" {
  for_each = var.postgressql != {} ? var.regions : {}

  source = "../../../dtos-devops-templates/infrastructure/modules/postgressql-flexible"

  # Azure SQL Server
  name                = module.regions_config[each.key].names.postgres-sql-server
  resource_group_name = azurerm_resource_group.core[each.key].name
  location            = each.key

  backup_retention_days           = var.postgressql.backup_retention_days
  geo_redundant_backup_enabled    = var.postgressql.geo_redundant_backup_enabled
  postgresql_admin_object_id      = data.azuread_group.postgres_sql_admin_group.object_id
  postgresql_admin_principal_name = var.postgressql.postgres_sql_admin_group
  postgresql_admin_principal_type = "Group"
  public_network_access_enabled   = var.postgressql.public_network_access_enabled

  sku_name     = var.postgressql.dbs.commgt.sku_name
  storage_mb   = var.postgressql.dbs.commgt.storage_mb
  storage_tier = var.postgressql.dbs.commgt.storage_tier

  server_version = var.postgressql.server_version
  tenant_id      = data.azurerm_client_config.current.tenant_id
  zone           = var.postgressql.zone

  # postgresql_configurations
  postgresql_configurations = {}


  # Private Endpoint Configuration if enabled
  private_endpoint_properties = var.features.private_endpoints_enabled ? {
    private_dns_zone_ids_sql             = [data.terraform_remote_state.hub.outputs.private_dns_zones["${each.key}-postgres_sql"].id]
    private_endpoint_enabled             = var.features.private_endpoints_enabled
    private_endpoint_subnet_id           = module.subnets["${module.regions_config[each.key].names.subnet}-pep"].id
    private_endpoint_resource_group_name = azurerm_resource_group.rg_private_endpoints[each.key].name
    private_service_connection_is_manual = var.features.private_service_connection_is_manual
  } : null

  databases = {
    db1 = {
      collation   = "en_US.utf8"
      charset     = "UTF8"
      max_size_gb = 10
      name        = "example_database_1"
    }
  }

  tags = var.tags
}

data "azuread_group" "postgres_sql_admin_group" {
  #display_name = "GRZ-Digital-Screening-DToS-Contributors"
  display_name = var.postgressql.postgres_sql_admin_group
}
