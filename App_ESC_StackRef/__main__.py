# Copyright 2016-2021, Pulumi Corporation.  All rights reserved.

import pulumi
import pulumi_azure_native.authorization as authorization
import pulumi_azure_native.documentdb as documentdb
import pulumi_azure_native.logic as logic
import pulumi_azure_native.web as web

## uncomment this line to use inline stack reference
import config




### Now deploy the app using the outputs from the referenced stack

account_keys = documentdb.list_database_account_keys_output(
    account_name=config.cosmosdb_account_name,
    resource_group_name=config.resource_group_name)

client_config = pulumi.Output.from_input(authorization.get_client_config())

api_id = pulumi.Output.concat(
    "/subscriptions/", client_config.subscription_id,
    "/providers/Microsoft.Web/locations/", config.resource_group_location,
    "/managedApis/documentdb")

# API Connection to be used in a Logic App
connection = web.Connection(
    "connection",
    resource_group_name=config.resource_group_name,
    properties=web.ApiConnectionDefinitionPropertiesArgs(
        display_name="cosmosdb_connection",
        api=web.ApiReferenceArgs(
            id=api_id,
        ),
        parameter_values={
            "databaseAccount": config.cosmosdb_account_name,
            "accessKey": account_keys.primary_master_key,
        },
    ))

# Logic App with an HTTP trigger and Cosmos DB action
workflow = logic.Workflow(
    "workflow",
    resource_group_name=config.resource_group_name,
    definition={
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "$connections": {
                "defaultValue": {},
                "type": "Object",
            },
        },
        "triggers": {
            "Receive_post": {
                "type": "Request",
                "kind": "Http",
                "inputs": {
                    "method": "POST",
                    "schema": {
                        "properties": {},
                        "type": "object",
                    },
                },
            },
        },
        "actions": {
            "write_body": {
                "type": "ApiConnection",
                "inputs": {
                    "body": {
                        "data": "@triggerBody()",
                        "id": "@utcNow()",
                    },
                    "host": {
                        "connection": {
                            "name": "@parameters('$connections')['documentdb']['connectionId']",
                        },
                    },
                    "method": "post",
                    "path": pulumi.Output.all(config.db_name, config.db_container_name).apply(
                        lambda arg: f"/dbs/{arg[0]}/colls/{arg[1]}/docs"),
                },
            },
        },
    },
    parameters={
        "$connections": logic.WorkflowParameterArgs(
            value={
                "documentdb": {
                    "connectionId": connection.id,
                    "connection_name": "logicapp-cosmosdb-connection",
                    "id": api_id,
                },
            },
        ),
    })


callback_urls = logic.list_workflow_trigger_callback_url_output(
    resource_group_name=config.resource_group_name,
    workflow_name=workflow.name,
    trigger_name="Receive_post")


# Export the HTTP endpoint
pulumi.export("endpoint", callback_urls.value)
