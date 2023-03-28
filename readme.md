Azure stuffs:

Create an Azure Active Directory (Azure AD) application: To authenticate to Azure using Python, you need to create an Azure AD application and assign it a role with the necessary permissions. Follow the instructions in the Azure documentation to create an Azure AD application and assign it a role with the necessary permissions.
https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal
Get the application credentials: After you create the Azure AD application, you need to get the application credentials, which include the client ID and client secret. Follow the instructions in the Azure documentation to get the client ID and client secret for your Azure AD application.
https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#get-values-for-signing-in
Get the subscription ID: To interact with Azure resources, you also need the subscription ID of your Azure account. Follow the instructions in the Azure documentation to get the subscription ID.
https://docs.microsoft.com/en-us/azure/cost-management-billing/manage/create-subscription
Get the tenant ID: Finally, you need the tenant ID of your Azure AD directory to authenticate to Azure. Follow the instructions in the Azure documentation to get the tenant ID.
https://docs.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-how-to-find-tenant
Once you have the client ID, client secret, subscription ID, and tenant ID, you can use them to authenticate to Azure using the Azure SDK for Python.


Settings:
Provide the azure config file path in the .env file.
TRANSCRIPTION_DIRECTORY is the folder where the audio files are stored, which will be transcribed.
TRANSCRIPTION_OUTPUT_DIRECTORY is the folder where the transcription output will be stored in text format.