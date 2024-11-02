# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:
**Testing & development**
| Azure Resource            | Service Tier                           | Monthly Cost                         |
| ------------------------- | -------------------------------------- | ------------------------------------ |
| *Azure Postgres Database* | Burstable                              |  $16.09                              |
| *Azure Service Bus*       | Basic                                  |  $0.05 per 1M operations per 1 month |
| *Azure Storage account*   | Standard performance - Cool tier       |  $0.01 per GB per month              |
| *Azure App Service*       | Basic (B1)                             |  $12,41                              |
| *Azure Function*          | EP1                                    |  vCPU: $116.80 vCPU/month            |

**Production-level environment**
| Azure Resource            | Service Tier                           | Monthly Cost                         |
| ------------------------- | -------------------------------------- | ------------------------------------ |
| *Azure Postgres Database* | Flexible (GP_Gen5_2)                   |  $226.92                             |
| *Azure Service Bus*       | Standard                               |  $10.80 per 1M operations per month  |
| *Azure Storage account*   | Standard performance - Hot tier        |  $0.144                              |
| *Azure App Service*       | Premium (P1v3)                         |  $93.80                              |
| *Azure Function*          | EP1                                    |  vCPU: $116.80 vCPU/month            |

Explain:
+ Azure Postgres Database - Flexible GP_Gen5_2: Provides better performance and scalability
+ Azure Service Bus - Standard: High messages
+ Azure Storage Account - Standard performance + Hot tier: Cost-effective storage for accessed data
+ Azure App Service - Premium P1v3: Offers better performance and scalability.
+ Azure Function - EP1: Ensures reliable and scalable function execution

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

**Drawbacks of Previous Architecture**
In the previous project, email notifications sent directly through the web app. This design has issues when dealing with a large number of attendees
+ Timeout Errors: Users can wait on the notification page for emails to be sent to 1000+ attendees, can have many timeout errors
+ Performance: The web app became a single point of failure for email processing, degrading overall performance

**Advantages of the Current Architecture**
The current architecture utilizes Azure services to improve functionality:
+ Azure Functions: Reducing load and timeout errors.  
+ Service Bus Queue: Manages notifications efficiently, can handle email processing without system overload
+ Scalability: Scale independently, enhancing performance and reliability

**Explain the Azure resources used in the current architecture to overcome the drawbacks**
1. Azure Service Bus: A messaging service ensures delivery of messages and allows for the decoupling of components.
2. Azure Database for PostgreSQL: high availability and scalability with many features