terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "hr-copilot-github-rg"
    storage_account_name = "hrcopilottfstatee969ca"
    container_name       = "tfstate"
    key                  = "hr-copilot.tfstate"
    use_azuread_auth     = true
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}
