import pulumi

# Stack Config
config = pulumi.Config()

# Outputs from the base stack abstracted via an ESC environment and thus appears to the program as regular stack config.
cosmosdb_account_name = config.require("cosmosdb_account_name")
resource_group_name = config.require("resource_group_name")
resource_group_location = config.require("resource_group_location")
db_name = config.require("db_name")
db_container_name = config.require("db_container_name")