locals {
  primary_region = [for k, v in var.regions : k if v.is_primary_region][0]

  environment_short = substr(var.environment, 0, 3)
}
