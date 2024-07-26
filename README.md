# Google Drive Folder Copy (copy_gdrive_folder.py)

This script -- `copy_gdrive_folder.py` -- recursively copies the contents of a source folder to a temporary location within the organization's Google Drive, and then moves the content to a specified Shared Drive. It uses a Google service account to impersonate a specified user.

The need for this script came from a scenario in my org where we had been providing some file-share space to a working group we were involved in. Most of the members of this group were external to the org; this also dates back to before Google introduced, "Shared Drives," as their preferred method for external file sharing. 

Moving content from a Google Drive "organization" shared folder to a "Shared Drive" is a royal PITA, especially for those of us who have had a Google Apps setup prior to "Shared Drive" functionality. If you are a glutton for punishment I'd encourage you to take a deep dive into the byzantine web of mostly out-of-date garbage that a search will get you. And please don't get me started on Google's own - and I utter this term with 
a large vein pulsating above my left eye - "documentation". 

For those who don't enjoy shoving a hot poker into your choice of sensitive orafice, the summary is that in most cases it is **actually impossible** to directly move organization shared folders into Shared Drives, especially if items were created by users **outside** the org. It doesn't matter whether you are a super-admin or minor deity or whatever; it is just not the way we [do things around here](https://support.google.com/drive/answer/13045066?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Cmove-files-owned-by-users-outside-of-your-organization). This is why it is really important to make sure your users understand the implications of sharing files within their own Google Drive. It is also why you might want to carefully consider the [Google Drive](https://2.5admins.com/2-5-admins-173/) [value](https://arstechnica.com/gadgets/2023/04/google-drive-cancels-its-surprise-file-cap-promises-to-communicate-better/) [proposition](https://www.techopedia.com/news/google-denies-gemini-ingests-drive-files). 

The somewhat convulated way that this script circumvents the problem, ahem, _feature_ is to copy the contents to a temporary 
location **inside** the org, change ownership permissions to a domain user, then copy them again to the target Shared Drive. It also must recreate the folder "structure" (yeah, I know, it's a flat namespace; but try explaining 
that to your users) in the Shared Drive. 

In my own environment, I encountered a number of files that had strange permissions that meant they could not be copied at all. In this case, these files are logged to a CSV file that can (hopefully) become someone else's problem.

**CAVEATS:**
- The big one is that the IDs (i.e., urls) of the files will change. If you need them to remain static which may very well be the case, this is the wrong solution for you. And best of luck.
- Existing share permissions, including ownership, will disappear. Depending on your specific situation, there are ways of automating this using the Google Drive API; but I didn't have that need myself.
- Workflow/versioning history will also, of course, reset as these will be new files.
- Most of this code was generated by GPT4o. If this is the kind of job that the robots want to take from me, they're free to have it.

## Features

- Copies the folder structure and files from a source folder to a temporary location.
- Moves the copied content from the temporary location to a Shared Drive.
- Logs any failed copy operations to a CSV file with a timestamp.

## Prerequisites

1. **Google Cloud Project**: Set up a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. **Enable Google Drive API**: Enable the Google Drive API for your project.
3. **Service Account**: Create a service account and download the JSON key file.
4. **Domain-Wide Delegation**: Grant domain-wide delegation to the service account and authorize it to impersonate users in your domain.
5. **Python Libraries**: Install the required Python libraries.

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pyyaml
```
(For additional info/background on configuring Google Drive API, see, `GoogleDriveAPISetup.md`, included in this repo.)

## Configuration
Create a config.yaml file with the following structure:

```yaml
service_account_file: 'path_to_your_service_account.json'
delegated_user_email: 'user@example.com'
source_folder_id: 'your_source_folder_id'
temp_parent_folder_id: 'your_temp_parent_folder_id'
shared_drive_folder_id: 'your_shared_drive_folder_id'
```

- `service_account_file`: Path to your service account JSON key file.
- `delegated_user_email`: The email of the user to impersonate.
- `source_folder_id`: The ID of the source folder you want to copy.
- `temp_parent_folder_id`: The ID of the temporary parent folder where the source folder will be copied.
- `shared_drive_folder_id`: The ID of the destination parent folder in the Shared Drive.

## Usage
1. **Clone the Repository**: Clone or download this repository to your local machine.

2. **Install Dependencies**: Install the required Python libraries (as shown above).

3. **Configure**: Create and fill out the config.yaml file with the appropriate values.

4. **Run the Script**: Execute the script using Python.

``` bash
python copy_gdrive_folder.py
```

## Script Details

### Script Overview
The script performs the following steps:

1. **Load Configuration**: Reads the configuration variables from the config.yaml file.
2. **Initialize API**: Authenticates and initializes the Google Drive API with impersonation.
3. **Copy to Temporary Location**: Recursively copies the source folder and its contents to a temporary location.
4. **Move to Shared Drive**: Recreates the folder structure in the Shared Drive and moves the copied files.
5. **Logging**: Logs any failed copy operations to a CSV file with a timestamp.

### Error Handling
Any failed copy operations are logged to a CSV file named `failed_copies_log_<timestamp>.csv`.
Errors encountered during file moves are printed to the console.

### Example config.yaml

``` yaml
service_account_file: 'path_to_your_service_account.json'
source_folder_id: '1A2B3C4D5E6F'
temp_parent_folder_id: '7G8H9I0J1K2L'
shared_drive_folder_id: '3M4N5O6P7Q8R'
delegated_user_email: 'admin@densho.us'
```

## Notes
Ensure that the service account has the necessary permissions to access the source folder and the Shared Drive.
The service account must be authorized for domain-wide delegation to impersonate the specified user.

## License
This project is licensed under the MIT License.
