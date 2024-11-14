locals {
  function_app_rbac_roles_key_vault = [
    "Key Vault Secrets User",
    "Key Vault Crypto User"
  ]

  terraform_mi_rbac_roles_key_vault = [
    "Key Vault Secrets User",
    "Key Vault Crypto User"
  ]
  
  function_app_rbac_roles_storage = [
    "Storage Account Contributor",
    "Storage Blob Data Owner",
    "Storage Queue Data Contributor"
  ]

  terraform_mi_rbac_roles_storage = [
    "Storage Account Contributor",
    "Storage Blob Data Owner",
    "Storage Queue Data Contributor"
  ]

}
