import pulumi
import pulumi_azure_native.documentdb as documentdb
import pulumi_azure_native.resources as resources
import pulumi_azure_native.storage as storage

config = pulumi.Config()
protect_flag = config.get_bool("protect_flag") or True

# Create an Azure Resource Group
# EXPLICITLY set the protect resource option to show what it looks like.
resource_group = resources.ResourceGroup("resourceGroup",
                                         opts=pulumi.ResourceOptions(protect=protect_flag))


# Use a stack transform to set the protect flag for the rest of the stack.
# Normally, this would be at the top of the file before any resources are created.
# But in the interest of showing the individual protect flag, we're doing it here.
# So registering this transform will apply the protect flag to all resources created after this point.
def transform(args: pulumi.ResourceTransformArgs):
        return pulumi.ResourceTransformResult(
            props=args.props,
            opts=pulumi.ResourceOptions.merge(args.opts, pulumi.ResourceOptions(
                protect=protect_flag,
            )))
pulumi.runtime.register_resource_transform(transform)

# Create an Azure resource (Storage Account)
storage_account = storage.StorageAccount(
    "logicappdemosa",
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2)

# Cosmos DB Account
cosmosdb_account = documentdb.DatabaseAccount(
    "logicappdemo-cdb",
    resource_group_name=resource_group.name,
    database_account_offer_type=documentdb.DatabaseAccountOfferType.STANDARD,
    locations=[documentdb.LocationArgs(
        location_name=resource_group.location,
        failover_priority=0,
    )],
    consistency_policy=documentdb.ConsistencyPolicyArgs(
        default_consistency_level=documentdb.DefaultConsistencyLevel.SESSION,
    ))

# Cosmos DB Database
db = documentdb.SqlResourceSqlDatabase(
    "sqldb",
    resource_group_name=resource_group.name,
    account_name=cosmosdb_account.name,
    resource=documentdb.SqlDatabaseResourceArgs(
        id="sqldb",
    ))

# Cosmos DB SQL Container
db_container = documentdb.SqlResourceSqlContainer(
    "container",
    resource_group_name=resource_group.name,
    account_name=cosmosdb_account.name,
    database_name=db.name,
    resource=documentdb.SqlContainerResourceArgs(
        id="container",
        partition_key=documentdb.ContainerPartitionKeyArgs(
            paths=["/myPartitionKey"],
            kind="Hash",
        )
    ))

### Stack Outputs
pulumi.export("cosmosdb_account_name", cosmosdb_account.name)
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("resource_group_location", resource_group.location)
pulumi.export("db_name", db.name)
pulumi.export("db_container_name", db_container.name) 
