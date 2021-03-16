
from pathlib import Path
from typing import List

from azure.storage.blob import BlobServiceClient, ContainerClient

from . import utils


CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;"
    "AccountName={};"
    "AccountKey={};"
    "EndpointSuffix={}"
)

class args:
    account_name = "codesearchtool"
    container_name = "git-annex"
    endpoint_suffix = "core.windows.net"


class AzureAPI:
    def __init__(self, connection_string: str) -> None:
        self.secret = connection_string

    def list_containers(self) -> List[str]:
        blob_service = BlobServiceClient.from_connection_string(conn_str=self.secret)
        containers_found = blob_service.list_containers()
        container_names = [container.name for container in containers_found]
        return container_names

    def list_blobs(self, container_name: str) -> List[str]:
        container_client = ContainerClient.from_connection_string(
            conn_str=self.secret, container_name=container_name
        )
        blobs_found = container_client.list_blobs()
        blob_names = [blob.name for blob in blobs_found]
        return blob_names

    def download(
        self, container_name: str, blob_name: str, path_to_download: Path
    ):
        blob_service_client = BlobServiceClient.from_connection_string(self.secret)
        container_client = blob_service_client.get_container_client(container_name)
        # try:
        blob_client = container_client.get_blob_client(blob_name)
        utils.mkdirs(path_to_download)
        with open(path_to_download, "wb") as my_blob:
            download_stream = blob_client.download_blob()
            download_stream.readinto(my_blob)
        # except Exception as e:
        #     if path_to_download.is_file():
        #         path_to_download.unlink()
        #     raise e

    def delete_blob(self, container_name: str, blob_name: str):
        blob_service_client = BlobServiceClient.from_connection_string(self.secret)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def delete_blob_and_container(self, container_name: str):
        container_client = ContainerClient.from_connection_string(
            conn_str=self.secret, container_name=container_name
        )
        container_client.delete_container()


def main():
    with open("azure-storage-blob-write.key") as f:
        key = f.read()
    conn_str = CONNECTION_STRING.format(
        args.account_name, key, args.endpoint_suffix
    )
    con = AzureAPI(conn_str)
    con.list_containers()
    blob_names = con.list_blobs('git-annex')
    print(blob_names)


if __name__ == "__main__":
    main()
