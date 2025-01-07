module "functionapp" {
  source = "../../../dtos-devops-templates/infrastructure/modules/function-app"

  function_app_name   = "${module.regions_config[local.primary_region].names.function-app}-${local.name_suffix}"
  resource_group_name = azurerm_resource_group.core[local.primary_region].name
  location            = local.primary_region

  app_settings = local.app_settings

  log_analytics_workspace_id                           = data.terraform_remote_state.audit.outputs.log_analytics_workspace_id[local.primary_region]
  monitor_diagnostic_setting_function_app_enabled_logs = local.monitor_diagnostic_setting_function_app_enabled_logs
  monitor_diagnostic_setting_function_app_metrics      = local.monitor_diagnostic_setting_function_app_metrics

  public_network_access_enabled = var.features.public_network_access_enabled
  vnet_integration_subnet_id    = module.subnets["${module.regions_config[local.primary_region].names.subnet}-apps"].id

  rbac_role_assignments = local.rbac_role_assignments

  asp_id = module.app-service-plan["${var.function_app.app_service_plan_key}-${local.primary_region}"].app_service_plan_id

  # Use the storage account assigned identity for the Function Apps:
  storage_account_name          = module.storage["fnapp-${local.primary_region}"].storage_account_name
  storage_account_access_key    = var.function_app.storage_uses_managed_identity == true ? null : module.storage["fnapp-${local.primary_region}"].storage_account_primary_access_key
  storage_uses_managed_identity = var.function_app.storage_uses_managed_identity

  # Connection string for Application Insights:
  ai_connstring = data.azurerm_application_insights.ai.connection_string

  # Use the ACR assigned identity for the Function Apps:
  cont_registry_use_mi = var.function_app.cont_registry_use_mi

  # Other Function App configuration settings:
  always_on    = var.function_app.always_on
  worker_32bit = var.function_app.worker_32bit

  acr_mi_client_id = data.azurerm_user_assigned_identity.acr_mi.client_id
  acr_login_server = data.azurerm_container_registry.acr.login_server

  # Use the ACR assigned identity for the Function Apps too:
  assigned_identity_ids = var.function_app.cont_registry_use_mi ? [data.azurerm_user_assigned_identity.acr_mi.id] : []

  image_tag  = var.function_app.docker_env_tag
  image_name = "${var.function_app.docker_img_prefix}-${lower(local.name_suffix)}"

  # Private Endpoint Configuration if enabled
  private_endpoint_properties = var.features.private_endpoints_enabled ? {
    private_dns_zone_ids                 = [data.terraform_remote_state.hub.outputs.private_dns_zones["${local.primary_region}-app_services"].id]
    private_endpoint_enabled             = var.features.private_endpoints_enabled
    private_endpoint_subnet_id           = module.subnets["${module.regions_config[local.primary_region].names.subnet}-pep"].id
    private_endpoint_resource_group_name = azurerm_resource_group.rg_private_endpoints[local.primary_region].name
    private_service_connection_is_manual = var.features.private_service_connection_is_manual
  } : null

  function_app_slots = var.function_app_slots

  tags = var.tags
}


locals {
  name_suffix    = "communication_management"
  primary_region = [for k, v in var.regions : k if v.is_primary_region][0]
  app_settings = merge(
    var.function_app.env_vars_static,
    {
      DOCKER_ENABLE_CI                    = var.function_app.docker_CI_enable
      FUNCTIONS_WORKER_RUNTIME            = "python"
      REMOTE_DEBUGGING_ENABLED            = var.function_app.remote_debugging_enabled
      WEBSITES_ENABLE_APP_SERVICE_STORAGE = var.function_app.enable_appsrv_storage
      WEBSITE_PULL_IMAGE_OVER_VNET        = var.features.private_endpoints_enabled

      DATABASE_NAME     = "communication_management"
      DATABASE_HOST     = "${module.regions_config[var.regions.keys[0]].names.postgres-sql-server}.postgres.database.azure.com"
      DATABASE_USER     = "commgt_db_user"
      DATABASE_PASSWORD = "@Microsoft.KeyVault(SecretUri=${module.postgresql_flexible_db[var.regions.keys[0]].db_admin_pwd_keyvault_secret})"

      APPLICATION_ID = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.application_id[var.regions.keys[0]].versionless_id})"
      NOTIFY_API_KEY = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.notify_api_key[var.regions.keys[0]].versionless_id})"
      OAUTH2_API_KID = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.oauth2_api_kid[var.regions.keys[0]].versionless_id})"
      OAUTH2_API_KEY = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.oauth2_api_key[var.regions.keys[0]].versionless_id})"
      PRIVATE_KEY    = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_key.private_key[var.regions.keys[0]].versionless_id})"
    }
  )

  rbac_role_assignments = flatten([
    var.key_vault != {} ? [
      for role in local.rbac_roles_key_vault_user : {
        role_definition_name = role
        scope                = module.key_vault[var.regions.keys[0]].key_vault_id
      }
    ] : [],
    [
      for account in keys(var.storage_accounts) : [
        for role in local.rbac_roles_storage : {
          role_definition_name = role
          scope                = module.storage["${account}-${var.regions.keys[0]}"].storage_account_id
        }
      ]
    ]
  ])
}
