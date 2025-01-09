application           = "commgt"
application_full_name = "communication-management"
environment           = "NFT"

features = {
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
    address_space     = "10.110.0.0/16"
    connect_peering   = true
    subnets = {
      pep = {
        cidr_newbits = 8
        cidr_offset  = 1
      }
    }
  }
}

app_insights = {
  appinsights_type = "web"
}

law = {
  law_sku        = "PerGB2018"
  retention_days = 30
}
