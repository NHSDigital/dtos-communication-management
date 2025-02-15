module "functionapp" {
  for_each = local.function_app_map

  source = "../../../dtos-devops-templates/infrastructure/modules/function-app"

  function_app_name   = "${module.regions_config[each.value.region].names.function-app}-${lower(each.value.name_suffix)}"
  resource_group_name = azurerm_resource_group.core[each.value.region].name
  location            = each.value.region

  app_settings = each.value.app_settings

  log_analytics_workspace_id                           = data.terraform_remote_state.audit.outputs.log_analytics_workspace_id[local.primary_region]
  monitor_diagnostic_setting_function_app_enabled_logs = local.monitor_diagnostic_setting_function_app_enabled_logs
  monitor_diagnostic_setting_function_app_metrics      = local.monitor_diagnostic_setting_function_app_metrics

  public_network_access_enabled = var.features.public_network_access_enabled
  vnet_integration_subnet_id    = module.subnets["${module.regions_config[each.value.region].names.subnet}-apps"].id

  rbac_role_assignments = each.value.rbac_role_assignments

  asp_id = module.app-service-plan["${each.value.app_service_plan_key}-${each.value.region}"].app_service_plan_id

  # Use the storage account assigned identity for the Function Apps:
  storage_account_name          = module.storage["fnapp-${each.value.region}"].storage_account_name
  storage_account_access_key    = var.function_apps.storage_uses_managed_identity == true ? null : module.storage["fnapp-${each.value.region}"].storage_account_primary_access_key
  storage_uses_managed_identity = var.function_apps.storage_uses_managed_identity

  # Connection string for Application Insights:
  ai_connstring = data.azurerm_application_insights.ai.connection_string

  # Use the ACR assigned identity for the Function Apps:
  cont_registry_use_mi = var.function_apps.cont_registry_use_mi

  # Other Function App configuration settings:
  always_on    = var.function_apps.always_on
  worker_32bit = var.function_apps.worker_32bit

  acr_mi_client_id = data.azurerm_user_assigned_identity.acr_mi.client_id
  acr_login_server = data.azurerm_container_registry.acr.login_server

  # Use the ACR assigned identity for the Function Apps too:
  assigned_identity_ids = var.function_apps.cont_registry_use_mi ? [data.azurerm_user_assigned_identity.acr_mi.id] : []

  image_tag  = var.function_apps.docker_env_tag
  image_name = "${var.function_apps.docker_img_prefix}-${lower(each.value.name_suffix)}"

  # Private Endpoint Configuration if enabled
  private_endpoint_properties = var.features.private_endpoints_enabled ? {
    private_dns_zone_ids                 = [data.terraform_remote_state.hub.outputs.private_dns_zones["${each.value.region}-app_services"].id]
    private_endpoint_enabled             = var.features.private_endpoints_enabled
    private_endpoint_subnet_id           = module.subnets["${module.regions_config[each.value.region].names.subnet}-pep"].id
    private_endpoint_resource_group_name = azurerm_resource_group.rg_private_endpoints[each.value.region].name
    private_service_connection_is_manual = var.features.private_service_connection_is_manual
  } : null

  function_app_slots = var.function_app_slots

  tags = var.tags
}


locals {

  app_settings_common = {
    DOCKER_ENABLE_CI                    = var.function_apps.docker_CI_enable
    REMOTE_DEBUGGING_ENABLED            = var.function_apps.remote_debugging_enabled
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = var.function_apps.enable_appsrv_storage
    WEBSITE_PULL_IMAGE_OVER_VNET        = var.features.private_endpoints_enabled
    FUNCTIONS_WORKER_RUNTIME            = "python"
  }

  # There are multiple Function Apps and possibly multiple regions.
  # We cannot nest for loops inside a map, so first iterate all permutations of both as a list of objects...
  function_app_config_object_list = flatten([
    for region in keys(var.regions) : [
      for function, config in var.function_apps.fa_config : merge(
        {
          region   = region   # 1st iterator
          function = function # 2nd iterator
        },
        config, # the rest of the key/value pairs for a specific function
        {
          app_settings = merge(
            local.app_settings_common,
            config.env_vars_static,

            # Dynamic env vars which cannot be stored in tfvars file
            function == "message-status" ? {
              APPLICATION_ID = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.application_id[region].versionless_id})"
              NOTIFY_API_KEY = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.notify_api_key[region].versionless_id})"
            } : {},
            function == "notify" ? {
              OAUTH2_API_KID = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.oauth2_api_kid[region].versionless_id})"
              OAUTH2_API_KEY = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_secret.oauth2_api_key[region].versionless_id})"
              PRIVATE_KEY    = "@Microsoft.KeyVault(SecretUri=${data.azurerm_key_vault_key.private_key[region].versionless_id})"
            } : {},
            function == "process-pilot-data" ? {
              AzureWebJobsStorage__accountName = module.storage["fnapp-${region}"].storage_account_name
              NOTIFY_FUNCTION_URL = format(
                "https://%s-%s.azurewebsites.net/api/%s/message/send",
                module.regions_config[region].names["function-app"],
                var.function_apps.fa_config["notify"].name_suffix,
                lower(var.function_apps.fa_config["notify"].function_endpoint_name)
              )
            } : {},

            # Dynamic reference to Key Vault
            length(config.key_vault_url) > 0 ? {
              (config.key_vault_url) = module.key_vault[region].key_vault_url
            } : {},

            # Database
            config.database_required ? {
              DATABASE_NAME     = "communication_management"
              DATABASE_HOST     = "${module.regions_config[region].names.postgres-sql-server}.postgres.database.azure.com"
              DATABASE_USER     = "commgt_db_user"
              DATABASE_PASSWORD = "@Microsoft.KeyVault(SecretUri=${module.postgresql_flexible_db[region].db_admin_pwd_keyvault_secret})"
              # DATABASE_USER     = var.postgresql.postgres_sql_admin_group
            } : {}

          )

          # These RBAC assignments are for the Function Apps only
          rbac_role_assignments = flatten([

            # Key Vault
            var.key_vault != {} ? [
              for role in local.rbac_roles_key_vault_user : {
                role_definition_name = role
                scope                = module.key_vault[region].key_vault_id
              }
            ] : [],

            # Storage Accounts
            [
              for account in keys(var.storage_accounts) : [
                for role in local.rbac_roles_storage : {
                  role_definition_name = role
                  scope                = module.storage["${account}-${region}"].storage_account_id
                }
              ]
            ]
          ])
        }
      )
    ]
  ])

  # ...then project the list of objects into a map with unique keys (combining the iterators), for consumption by a for_each meta argument
  function_app_map = {
    for object in local.function_app_config_object_list : "${object.function}-${object.region}" => object
  }
}
