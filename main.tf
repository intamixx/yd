# Configure Terraform
terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.15.0"
    }
    rke = {
      source  = "rancher/rke"
      version = "1.5.0"
    }
  }
}

#variable "server_names" {
#  type    = list(string)
#  default = ["k8-01", "k8-02"]
#  #count     = length(var.server_names)
#}

provider "azurerm" {
  skip_provider_registration = true
  subscription_id            = "3b9bccfa-ae80-4d20-a477-761db633f2e9"
  features {}
}
