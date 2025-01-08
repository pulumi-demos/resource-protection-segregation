# Azure Cosmos DB, an API Connection, and a Logic App - Multistack Approach

This is a multi-stack version of this example: https://github.com/pulumi/examples/tree/master/azure-py-cosmosdb-logicapp 

It is used to show how stack references and the protect flag can be used to protect and segregate stacks/resources.

## Pulumi Projects In the Repo

The `BaseInfra` project deploys the Resource Group, and CosmosDB.

The `App_InLine_StackRef` project uses a [stack reference](https://www.pulumi.com/docs/iac/concepts/stacks/#stackreferences) in the code to be able to deploy the web connection and workflow for the app on top of the `BaseInfra` stack.

The `App_ESC_StackRef` projects uses an [ESC Environment](https://www.pulumi.com/docs/esc/environments/) and the ESC [stacks provider](https://www.pulumi.com/docs/esc/integrations/infrastructure/pulumi-iac/pulumi-stacks/) to project the `BaseInfra` stack outputs to the `App_ESC_StackRef` stack as stack config.


## Prerequisites

1. [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
1. [Configure Pulumi for Azure](https://www.pulumi.com/docs/intro/cloud-providers/azure/setup/)
1. [Configure Pulumi for Python](https://www.pulumi.com/docs/intro/languages/python/)

## Set up the Environment

1. Login to Azure
    ```bash
    $ pulumi config set azure-native:location westeurope
    $ az login
    ```

## Deploy the `BaseInfra` Project

1. Create a new stack:

    ```sh
    $ cd BaseInfra
    $ pulumi stack init dev
    ```

1. Create a Python virtualenv, activate it, and install dependencies:

   This installs the dependent packages [needed](https://www.pulumi.com/docs/intro/concepts/how-pulumi-works/) for our Pulumi program.

    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    ```

1. Set the required configuration variables for this program, and log into Azure:

    ```bash
    $ pulumi config set azure-native:location centralus
    ```

1. Perform the deployment:

    ```sh
    $ pulumi up
    ```

## Deploy the `App_InLine_StackRef` Project

1. Create a new stack:

    ```sh
    $ cd App_InLine_StackRef
    $ pulumi stack init dev
    ```

1. Create a Python virtualenv, activate it, and install dependencies:

   This installs the dependent packages [needed](https://www.pulumi.com/docs/intro/concepts/how-pulumi-works/) for our Pulumi program.

    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    ```

1. Set the required configuration variables for this program, and log into Azure:

    ```bash
    $ pulumi config set azure-native:location centralus
    $ pulumi config set azure-cosmosdb-app:baseProjectName azure-cosmosdb-base
    ```

1. Perform the deployment:

    ```sh
    $ pulumi up
    ```

## Deploy the `App_ESC_StackRef` Project

1. Create a new stack:

    ```sh
    $ cd App_ESC_StackRef
    $ pulumi stack init dev
    ```

1. Create a Python virtualenv, activate it, and install dependencies:

   This installs the dependent packages [needed](https://www.pulumi.com/docs/intro/concepts/how-pulumi-works/) for our Pulumi program.

    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    ```

1. Create the ESC Environment to Reference the `BaseInfra` Stack

   Using the YAML below, create an environment in the Pulumi UI or by using `pulumi env init [<org-name>/][<project-name>/]<environment-name> -f FILE_WITH_BELOW_YAML`.


    ```
    # Use the stacks provider to get and project the kubeconfig from the given K8s cluster stack.
    values:
        stack-outputs:
            fn::open::pulumi-stacks:
                stacks:
                    cosmosdb-base-infra:
                        # Set this to the name of the stack being referenced
                        stack: azure-cosmosdb-base/dev
        pulumiConfig:
            cosmosdb_account_name: ${stack-outputs.cosmosdb-base-infra.cosmosdb_account_name}
            resource_group_name: ${stack-outputs.cosmosdb-base-infra.resource_group_name}
            resource_group_location: ${stack-outputs.cosmosdb-base-infra.resource_group_location}
            db_name: ${stack-outputs.cosmosdb-base-infra.db_name}
            db_container_name: ${stack-outputs.cosmosdb-base-infra.db_container_name}
    ```

1. Set the required configuration variables for this program, and log into Azure:

    ```bash
    $ pulumi config set azure-native:location centralus
    ```

    Edit the stack config file (e.g. `Pulumi.dev.yaml`) with:
    ```
    environment
      - PROJECT/ENVIRONMENT
    ```

    Where `PROJECT/ENVIRONMENT` references the environment created above.

1. Perform the deployment:

    ```sh
    $ pulumi up
    ```


## Using the Infrastruture

1. At this point, you have a Cosmos DB collection and a Logic App listening to HTTP requests. You can trigger the Logic App with a `curl` command:

    ```
    $ cd AppProject
    $ curl -X POST "$(pulumi stack output endpoint)" -d '"Hello World"' -H 'Content-Type: application/json'
    ```

    The POST body will be saved into a new document in the Cosmos DB collection.

1. Once you are done, you can destroy all resources and stacks by running the following in the `AppProject` folder and then the `BaseProject` folder:

    ```bash
    $ pulumi destroy
    $ pulumi stack rm
    ```
