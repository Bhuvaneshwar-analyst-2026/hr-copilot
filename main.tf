resource "azurerm_resource_group" "main" {
  name     = "hrcopilot-dev-rg"
  location = "East US"
}

resource "azurerm_storage_account" "docs" {
  name                     = "hrcopilotdevdocs"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_search_service" "search" {
  name                = "hrcopilot-dev-search"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "free"
}

resource "azurerm_key_vault" "kv" {
  name                      = "hrcopilot-dev-kv"
  resource_group_name       = azurerm_resource_group.main.name
  location                  = azurerm_resource_group.main.location
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
}

resource "azurerm_storage_table" "employees" {
  name                 = "Employees"
  storage_account_name = azurerm_storage_account.docs.name
}

resource "azurerm_service_plan" "app" {
  name                = "hrcopilot-dev-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "agent" {
  name                = "hrcopilot-dev-app"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.app.id

  app_settings = {
  SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
}

  site_config {
    app_command_line = "gunicorn --bind=0.0.0.0:8000 app:app"

    application_stack {
      python_version = "3.11"
    }
  }

  identity {
    type = "SystemAssigned"
  }
}
