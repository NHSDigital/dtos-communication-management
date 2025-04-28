output "application_insights" {
  value = {
    name                = module.app_insights_audit[local.primary_region].name
    resource_group_name = module.app_insights_audit[local.primary_region].resource_group_name
  }
}

output "log_analytics_workspace_id" {
  value = { for k, v in module.log_analytics_workspace_audit : k => v.id }
}
