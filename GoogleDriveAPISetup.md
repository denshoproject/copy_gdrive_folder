# Setting Up Google Drive API Service Account and Configuring Domain User Impersonation

This guide provides step-by-step instructions on setting up a Google Drive API service account and configuring it for domain-wide delegation to impersonate domain users.

## Prerequisites

1. **Google Cloud Project**: Ensure you have a Google Cloud project.
2. **Admin Access**: You need admin access to the Google Workspace admin console.

## Steps

### 1. Set Up Google Drive API

1. **Go to the Google Cloud Console**: [Google Cloud Console](https://console.cloud.google.com/).

2. **Create a New Project**:
    - Click on the project dropdown at the top of the page.
    - Click on "New Project".
    - Enter the project name and other details, then click "Create".

3. **Enable Google Drive API**:
    - Select your project.
    - In the left sidebar, navigate to `APIs & Services` > `Library`.
    - Search for "Google Drive API".
    - Click on "Google Drive API" and then click "Enable".

### 2. Create Service Account

1. **Go to the Service Accounts Page**:
    - In the left sidebar, navigate to `APIs & Services` > `Credentials`.
    - Click on `Create Credentials` > `Service account`.

2. **Create Service Account**:
    - Enter the service account name, ID, and description.
    - Click "Create and Continue".
    - Assign roles as needed (e.g., Project > Editor).

3. **Create Key for the Service Account**:
    - Click on the service account you just created.
    - Go to the `Keys` tab.
    - Click `Add Key` > `Create New Key`.
    - Select `JSON` and click `Create`. The key file will be downloaded automatically.

### 3. Enable Domain-Wide Delegation

1. **Edit Service Account**:
    - Go to the service account you created.
    - Click `Show Domain-Wide Delegation` (if not already shown).
    - Enable `Enable G Suite Domain-wide Delegation`.
    - Save the changes.

2. **Grant Domain-Wide Delegation**:
    - Note the `Client ID` of the service account.
    - Go to the [Google Admin console](https://admin.google.com/).
    - Navigate to `Security` > `API Controls` > `Manage Domain-Wide Delegation`.
    - Click `Add New`.
    - Enter the `Client ID` noted earlier.
    - In the OAuth Scopes field, enter the required scopes. For Google Drive, use:
      ```
      https://www.googleapis.com/auth/drive
      ```
    - Click `Authorize`.

### 4. Use the Service Account to Impersonate a User

1. **Install Required Libraries**:
    ```bash
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```

2. **Authenticate and Use the Service Account in Your Script**:

    ```python
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    # Path to your service account key file
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'

    # Scopes for accessing Google Drive
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # The email of the user to impersonate
    DELEGATED_USER_EMAIL = 'user_to_impersonate@example.com'

    # Authenticate and initialize the API with impersonation
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER_EMAIL
    )
    service = build('drive', 'v3', credentials=credentials)

    # Example: List the first 10 files the impersonated user has access to
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(f"{item['name']} ({item['id']})")
    ```

## Notes

- Ensure that the service account has the necessary permissions to perform actions on behalf of the impersonated user.
- The service account must be granted domain-wide delegation in the Google Workspace admin console.

## Additional Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Admin Console](https://admin.google.com/)
- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
