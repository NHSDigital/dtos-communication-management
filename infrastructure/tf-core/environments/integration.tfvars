application = "commgt"
environment = "INT"

features = {
  acr_enabled                          = false
  api_management_enabled               = false
  event_grid_enabled                   = false
  private_endpoints_enabled            = true
  private_service_connection_is_manual = false
  public_network_access_enabled        = false
}

tags = {
  Project = "Communication-Management"
}

regions = {
  uksouth = {
    is_primary_region = true
    address_space     = "10.111.0.0/16"
    connect_peering   = true
    subnets = {
      apps = {
        cidr_newbits               = 8
        cidr_offset                = 2
        delegation_name            = "Microsoft.Web/serverFarms"
        service_delegation_name    = "Microsoft.Web/serverFarms"
        service_delegation_actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
      }
      pep = {
        cidr_newbits = 8
        cidr_offset  = 1
      }
      db = {
        cidr_newbits = 8
        cidr_offset  = 3
      }
    }
  }
}

routes = {
  uksouth = {
    firewall_policy_priority = 100
    application_rules        = []
    nat_rules                = []
    network_rules = [
      {
        name                  = "AllowCommgtToAudit"
        priority              = 900
        action                = "Allow"
        rule_name             = "CommgtToAudit"
        source_addresses      = ["10.111.0.0/16"]
        destination_addresses = ["10.112.0.0/16"]
        protocols             = ["TCP", "UDP"]
        destination_ports     = ["443"]
      },
      {
        name                  = "AllowAuditToCommgt"
        priority              = 910
        action                = "Allow"
        rule_name             = "AuditToCommgt"
        source_addresses      = ["10.112.0.0/16"]
        destination_addresses = ["10.111.0.0/16"]
        protocols             = ["TCP", "UDP"]
        destination_ports     = ["443"]
      }
    ]
    route_table_routes_to_audit = [
      {
        name                   = "CommgtToAudit"
        address_prefix         = "10.112.0.0/16"
        next_hop_type          = "VirtualAppliance"
        next_hop_in_ip_address = "" # will be populated with the Firewall Private IP address
      }
    ]
    route_table_routes_from_audit = [
      {
        name                   = "AuditToCommgt"
        address_prefix         = "10.111.0.0/16"
        next_hop_type          = "VirtualAppliance"
        next_hop_in_ip_address = "" # will be populated with the Firewall Private IP address
      }
    ]
  }
}

app_service_plan = {
  os_type                  = "Linux"
  sku_name                 = "P2v3"
  vnet_integration_enabled = true

  autoscale = {
    memory_percentage = {
      metric = "MemoryPercentage"

      capacity_min = "1"
      capacity_max = "5"
      capacity_def = "1"

      time_grain       = "PT1M"
      statistic        = "Average"
      time_window      = "PT10M"
      time_aggregation = "Average"

      inc_operator        = "GreaterThan"
      inc_threshold       = 70
      inc_scale_direction = "Increase"
      inc_scale_type      = "ChangeCount"
      inc_scale_value     = 1
      inc_scale_cooldown  = "PT5M"

      dec_operator        = "LessThan"
      dec_threshold       = 25
      dec_scale_direction = "Decrease"
      dec_scale_type      = "ChangeCount"
      dec_scale_value     = 1
      dec_scale_cooldown  = "PT5M"
    }
  }

  instances = {
    Default = {}
  }
}

function_app = {
  acr_mi_name = "dtos-communication-management-acr-push"
  acr_name    = "acrukshubdevcommgt"
  acr_rg_name = "rg-hub-dev-uks-commgt"

  app_service_logs_disk_quota_mb         = 35
  app_service_logs_retention_period_days = 7

  always_on = true

  cont_registry_use_mi = true

  docker_CI_enable  = "true"
  docker_env_tag    = "integration"
  docker_img_prefix = "communication-management"

  enable_appsrv_storage         = "false"
  ftps_state                    = "Disabled"
  https_only                    = true
  remote_debugging_enabled      = false
  storage_uses_managed_identity = null
  worker_32bit                  = false

  app_service_plan_key = "Default"
  key_vault_url        = "KEY_VAULT_URL"
  app_urls             = []
  env_vars_static = {
    NOTIFY_API_URL   = "https://int.api.service.nhs.uk"
    OAUTH2_TOKEN_URL = "https://int.api.service.nhs.uk/oauth2/token"
    ENVIRONMENT      = "INTEGRATION"
  }
}

function_app_slots = []

key_vault = {
  disk_encryption   = true
  soft_del_ret_days = 7
  purge_prot        = false
  sku_name          = "standard"
}

diagnostic_settings = {
  metric_enabled = true
}

storage_accounts = {
  fnapp = {
    name_suffix                   = "fnappstor"
    account_tier                  = "Standard"
    replication_type              = "LRS"
    public_network_access_enabled = false
    containers = {
      file-upload-data = {
        container_name        = "file-upload-data"
        container_access_type = "private"
      }
    }
  }
}

postgresql = {
  postgres_sql_admin_group      = "postgresql_commgt_int_uks_admin"
  backup_retention_days         = 30
  geo_redundant_backup_enabled  = false
  public_network_access_enabled = false
  server_version                = 16
  zone                          = 1

  # commgt database
  dbs = {
    commgt = {
      storage_tier = "P10"
      storage_mb   = 32768
      sku_name     = "GP_Standard_D2s_v3"
    }
  }

  # fw_rules = {}
}
