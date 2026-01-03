from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Test Drive API with minimal setup
def minimal_drive_test():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    token_path = os.path.join(dir_path, 'token.json')

    creds = service_account.Credentials.from_service_account_file(
        token_path, 
        scopes=['https://www.googleapis.com/auth/drive'])

    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        pageSize=10, 
        fields="files(id, name)",
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    for file in results.get('files', []):
        print(f"Found file: {file.get('name')} with ID: {file.get('id')}")



def list_contents_of_folder(folder_id):
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the token file
    token_path = os.path.join(dir_path, 'token.json')

    # Use the token to authenticate
    creds = service_account.Credentials.from_service_account_file(
        token_path, 
        scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)

    # List files in the specified folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query, 
        pageSize=10, 
        fields="files(id, name)",
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    
    if files:
        for file in files:
            print(f"Found file: {file.get('name')} with ID: {file.get('id')}")
    else:
        print("No files found in the folder.")



def create_or_find_subfolder(parent_folder_id, subfolder_name):
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    # Check if the subfolder exists
    query = f"name = '{subfolder_name}' and '{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query, 
        fields="files(id, name)",
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    folders = results.get('files', [])

    if folders:
        print(f"Folder already exists: {folders[0]['name']} with ID: {folders[0]['id']}")
        return folders[0]['id']
    else:
        # Create the subfolder if it does not exist
        file_metadata = {
            'name': subfolder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(
            body=file_metadata, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        print(f"Created folder: {subfolder_name} with ID: {folder.get('id')}")
        return folder.get('id')


def upload_file_to_drive(folder_id, file_path, file_name):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # checking if files need updating
    
    # prepare the file metadata and the media upload object
    # prepare the file metadata and the media upload object
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)

    # check if a file with the same name exists in the folder
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    existing_files = service.files().list(
        q=query, 
        fields='files(id)',
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute().get('files', [])

    if existing_files:
        # if file exists, update it
        file_id = existing_files[0]['id']
        # For updates, we cannot include 'parents' field
        update_metadata = {'name': file_name}
        try:
            # Update the existing file with the new content
            file = service.files().update(
                fileId=file_id, 
                body=update_metadata, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            print(f"Updated file with ID: {file.get('id')}")
        except Exception as e:
            print(f"Failed to update {file_name}: {e}")
            return None
    else:
        # no existing file, upload as new
        try:
            file = service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            print(f"Uploaded new file with ID: {file.get('id')}")
            return file.get('id')
        except Exception as e:
            print(f"Failed to upload {file_name}: {e}")
            return None


def get_credentials():
    """Load credentials from a service account JSON file."""
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Construct the full path to the token file
    token_path = os.path.join(dir_path, 'token.json')

    # Use the token to authenticate
    credentials = service_account.Credentials.from_service_account_file(
        token_path, 
        scopes=['https://www.googleapis.com/auth/drive'])
    return credentials


def list_files_in_folder(folder_id):
    """List all files in a specific folder."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false", 
        fields="files(id, name)",
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    return files


def get_folder_size(folder_id):
    """
    Calculates the total size of all files in a specified Google Drive folder.

    Args:
    service: Authenticated Google Drive service object.
    folder_id (str): The ID of the Google Drive folder whose size you want to calculate.

    Returns:
    int: The total size of the files in the Google Drive folder in bytes.
    """
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    total_size = 0
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false", 
        fields="files(id, size)",
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    for file in files:
        total_size += int(file.get('size', 0))
    return total_size