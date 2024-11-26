locals {
  rbac_roles_key_vault = [
    "Key Vault Certificate User",
    "Key Vault Crypto User",
    "Key Vault Secrets User"
  ]

  rbac_roles_storage = [
    "Storage Account Contributor",
    "Storage Blob Data Owner",
    "Storage Queue Data Contributor"
  ]

}

module "user_rbac_assignments" {
  # This results in a numbered index, necessary to avoid keying on values that are only known after apply (scope is a resource id)
  for_each = { for idx, assignment in var.rbac_role_assignments : idx => assignment }

  source = "../../../dtos-devops-templates/infrastructure/modules/rbac-assignment"

  principal_id         = azurerm_linux_function_app.function_app.identity.0.principal_id
  role_definition_name = each.value.role_definition_name
  scope                = each.value.scope
}
