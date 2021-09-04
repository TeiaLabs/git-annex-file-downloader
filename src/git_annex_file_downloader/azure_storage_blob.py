import os
from pathlib import Path
from typing import List, Optional

from azure.storage.blob import BlobServiceClient, ContainerClient

from . import loggers, utils

logger = loggers.get_logger()


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

    def download(self, container_name: str, blob_name: str, path_to_download: Path):
        blob_service_client = BlobServiceClient.from_connection_string(self.secret)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        with open(path_to_download, "wb") as my_blob:
            download_stream = blob_client.download_blob()
            download_stream.readinto(my_blob)
        # TODO check download was good

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


def get_connection_string_from_env_var() -> Optional[str]:
    try:
        conn_str = os.environ["AZURE_CONNECTION_STRING"]
    except KeyError:
        return None
    return conn_str


def get_connection_string_from_key_file() -> Optional[str]:
    connection_str_template = (
        "DefaultEndpointsProtocol=https;"
        "AccountName={};"
        "AccountKey={};"
        "EndpointSuffix={}"
    )
    try:
        with open("azure-storage-blob-write.key") as f:
            key = f.read()
    except FileNotFoundError:
        return None
    conn_str = connection_str_template.format(
        args.account_name, key, args.endpoint_suffix
    )
    return conn_str


def get_connection_string() -> str:
    conn_str = get_connection_string_from_env_var()
    if not conn_str:
        conn_str = get_connection_string_from_key_file()
    if not conn_str:
        raise EnvironmentError
    return conn_str


def download_file(file_path: Path):
    symlink_path = Path(file_path)
    if symlink_path.is_symlink():
        file_key = utils.lookup_key(symlink_path)  # SHA256E-s1024--81a9ef8...
    else:
        raise ValueError(f"'{symlink_path}' is not a symlink.")
    file_size = utils.get_file_size_from_key(file_key)
    if not utils.needs_download(file_path, file_size):
        logger.info(f"Skipping already downloaded \n\t '{file_path}'.")
    else:
        conn_string = get_connection_string()
        azure = AzureAPI(conn_string)
        resolved_path = symlink_path.resolve()
        utils.mkdirs(resolved_path)
        logger.info(f"Downloading '{file_path}'...")
        azure.download(args.container_name, file_key, resolved_path)
    logger.info(f"ok")


def list_info():
    conn_str = get_connection_string()
    con = AzureAPI(conn_str)
    container_names = con.list_containers()
    print(container_names)
    blob_names = con.list_blobs("data")
    print(blob_names)


if __name__ == "__main__":
    list_info()
