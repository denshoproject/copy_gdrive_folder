import csv
import yaml
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

SERVICE_ACCOUNT_FILE = config['service_account_file']
SOURCE_FOLDER_ID = config['source_folder_id']
TEMP_PARENT_FOLDER_ID = config['temp_parent_folder_id']
SHARED_DRIVE_FOLDER_ID = config['shared_drive_folder_id']
DELEGATED_USER_EMAIL = config['delegated_user_email']

# Scopes for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate and initialize the API with impersonation
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES,
    subject=DELEGATED_USER_EMAIL
)
service = build('drive', 'v3', credentials=credentials)

# Counters for statistics
total_files = 0
successfully_copied_files = 0
failed_files = 0
failed_copies = []

def create_folder(name, parent_id):
    folder_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=folder_metadata, supportsAllDrives=True, fields='id').execute()
    return folder.get('id')

def copy_file(file_id, parent_id):
    global total_files, successfully_copied_files, failed_files
    total_files += 1

    file_metadata = service.files().get(fileId=file_id, fields='name').execute()
    new_file_metadata = {
        'name': file_metadata['name'],
        'parents': [parent_id]
    }
    try:
        service.files().copy(
            fileId=file_id,
            body=new_file_metadata,
            supportsAllDrives=True
        ).execute()
        successfully_copied_files += 1
    except Exception as e:
        failed_files += 1
        failed_copies.append({'id': file_id, 'name': file_metadata['name'], 'error': str(e)})

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)', supportsAllDrives=True).execute()
    return results.get('files', [])

def copy_folder(source_folder_id, destination_folder_id, folder_name):
    print(f'Copying folder: {folder_name}')
    items = list_files_in_folder(source_folder_id)

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            new_folder_id = create_folder(item['name'], destination_folder_id)
            copy_folder(item['id'], new_folder_id, item['name'])
        else:
            copy_file(item['id'], destination_folder_id)

def move_file(file_id, new_parent_id, old_parent_id):
    try:
        service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=old_parent_id,
            supportsAllDrives=True,
            fields='id, parents'
        ).execute()
    except Exception as e:
        print(f'An error occurred while moving {file_id}: {e}')

def log_failed_copies_to_csv(failed_copies, csv_filename):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'name', 'error'])
        writer.writeheader()
        for failure in failed_copies:
            writer.writerow(failure)

if __name__ == '__main__':
    # Record start time
    start_time = datetime.now()
    print(f'Start time: {start_time}')

    # Generate timestamp for the CSV log filename
    timestamp = start_time.strftime('%Y%m%d_%H%M%S')
    csv_filename = f'failed_copies_log_{timestamp}.csv'

    # Create the top-level folder in the temporary location
    source_folder_metadata = service.files().get(fileId=SOURCE_FOLDER_ID, fields='name').execute()
    temp_folder_id = create_folder(source_folder_metadata['name'], TEMP_PARENT_FOLDER_ID)

    # Start the recursive copy process to temporary location
    copy_folder(SOURCE_FOLDER_ID, temp_folder_id, source_folder_metadata['name'])

    # Now recreate the folder structure in the Shared Drive and move the files
    def recreate_and_move(source_folder_id, destination_folder_id):
        items = list_files_in_folder(source_folder_id)
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                new_folder_id = create_folder(item['name'], destination_folder_id)
                recreate_and_move(item['id'], new_folder_id)
            else:
                move_file(item['id'], destination_folder_id, source_folder_id)

    # Start the recursive move process to the Shared Drive
    recreate_and_move(temp_folder_id, SHARED_DRIVE_FOLDER_ID)

    # Record end time
    end_time = datetime.now()
    print(f'End time: {end_time}')

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(f'Total time elapsed: {elapsed_time}')

    # Print statistics
    print('Copy process completed.')
    print(f'Total files: {total_files}')
    print(f'Successfully copied files: {successfully_copied_files}')
    print(f'Failed to copy files: {failed_files}')
    
    if failed_files > 0:
        print(f'Logging failed copies to {csv_filename}')
        log_failed_copies_to_csv(failed_copies, csv_filename)
        print('Failed copies:')
        for failure in failed_copies:
            print(f"ID: {failure['id']}, Name: {failure['name']}, Error: {failure['error']}")
