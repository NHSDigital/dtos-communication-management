"""A script to send files to azurite
    Requirements:
        python-dotenv
        azure-storage-blob"""

import azure.storage.blob
import dotenv
import os
import sys


def send_file(file):
    try:
        dotenv.load_dotenv(dotenv_path=".env.local")
        blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(os.getenv('AZURITE_CONNECTION_STRING'))
        print("Connected to Azurite: " + os.getenv('AZURITE_CONNECTION_STRING'))
    except FileNotFoundError:
        sys.exit(".env.local not found, please create one based on .env.example.")
    except ValueError:
        sys.exit("AZURITE_CONNECTION_STRING not set in .env.local")

    pilot_data_client = blob_service_client.get_container_client(os.getenv('BLOB_CONTAINER_NAME'))
    file_name = os.path.basename(file)
    blob_client = pilot_data_client.get_blob_client(file_name)

    print("Blob client established for: " + os.getenv('BLOB_CONTAINER_NAME') + "/" + file_name)

    content_settings = azure.storage.blob.ContentSettings(content_type='text/csv')

    try:
        with open(file, "rb") as data:
            blob_client.upload_blob(data, blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
    except FileNotFoundError:
        sys.exit(f"File {file} could not been found")

    print(f"File {file} uploaded")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("""Description:
        A script to send files to azurite
    Usage:
        python send_file.py example.csv
    Arguments:
        file  The file to be sent to azurite
    CSV file format:
        The file should be a CSV file with no headings and the following columns:
        NHS number, Date of Birth, Appointment Date, Appointment Time, Appointment Address, Appointment Type""")
        sys.exit()
    else:
        file = sys.argv[1]

    send_file(file)
