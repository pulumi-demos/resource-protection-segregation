import pulumi

### Get stack reference and related outputs from the given stack.
# This could be done in a separate file and imported as a module.
# Also this assumes the org and stack names are the same.
# But one still needs to provide the name of the base project via config. 

# Stack Config
config = pulumi.Config()
base_project_name = config.require('baseProjectName')

# Stack Reference
base_stack_ref = pulumi.StackReference(f"{pulumi.get_organization()}/{base_project_name}/{pulumi.get_stack()}")

# Outputs from the referenced stack
cosmosdb_account_name = base_stack_ref.get_output("cosmosdb_account_name")
resource_group_name = base_stack_ref.get_output("resource_group_name")
resource_group_location = base_stack_ref.get_output("resource_group_location")
db_name = base_stack_ref.get_output("db_name")
db_container_name = base_stack_ref.get_output("db_container_name")