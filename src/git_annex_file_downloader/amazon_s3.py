import base64
from pathlib import Path
from typing import List, Optional, Union

import boto3

from . import loggers, utils
from .utils import raise_if_none, run_command, run_command_chain

logger = loggers.get_logger()


class args:
    bucket = "teia-codesearch-cryptopublic"
    encryption = "shared"
    mac_algo = "HMACSHA224"
    prefix = "crypto-public-s3/"
    remote_name = "crypto-public-s3"


@raise_if_none
def choose_remote(
    remotes_configs: List[str], remote_name: str
) -> Optional[str]:
    for remote in remotes_configs:
        if remote_name in remote:
            return remote
    return None


def decrypt_file(file_path: Union[Path, str], output_path: Union[Path, str]):
    remotes = get_remotes_config()
    special_remote = choose_remote(remotes, args.remote_name)
    cipher = get_cipher(special_remote)
    decryption_cipher = get_decryption_cipher(cipher).decode()
    run_command(
        f"gpg --quiet --batch --passphrase {decryption_cipher} --output - {file_path}",
        stdout=open(output_path, "wb")
    )


def download_from_s3(bucket_name: str, file_name: str, prefix: str):
    # s3 = boto3.client('s3')
    s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='')
    s3._request_signer.sign = (lambda *args, **kwargs: None)
    with open(f"/tmp/{file_name}", 'wb') as f:
        s3.download_fileobj(bucket_name, prefix + file_name, f)


def encrypt_key(
    annex_key: str, hmac_cipher: str, mac_algo: str = args.mac_algo
) -> str:
    commands = [
        f"echo -n '{annex_key}'",
        f"openssl dgst -{mac_algo.strip('HMAC')} -hmac '{hmac_cipher}'",
    ]
    openssl_output = run_command_chain(commands)
    encrypted_key = openssl_output.strip("(stdin)= ")
    return encrypted_key


@raise_if_none
def get_cipher(remote_config: str) -> Optional[str]:
    configs = remote_config.split(" ")
    keyword = "cipher="
    for conf in configs:
        if keyword in conf:
            return conf[len(keyword):]
    return None


def get_decryption_cipher(full_cipher: str) -> bytes:
    decoded = base64.decodebytes(full_cipher.encode())
    return decoded[256:-1]


def get_encrypted_key(file_path: Path) -> str:
    annex_key = utils.lookup_key(file_path)
    remotes = get_remotes_config()
    special_remote = choose_remote(remotes, args.remote_name)
    cipher = get_cipher(special_remote)
    hmac_cipher = get_hmac_cipher(cipher)
    partial_encrypted_key = encrypt_key(annex_key, hmac_cipher)
    partial_encrypted_key = partial_encrypted_key.strip("\n")
    full_encrypted_key = f"GPG{args.mac_algo}--{partial_encrypted_key}"
    return full_encrypted_key


def get_hmac_cipher(b64_full_cipher: str) -> str:
    full_cipher: bytes = base64.decodebytes(b64_full_cipher.encode())
    without_ln = full_cipher.strip(b"\n")
    cut = without_ln[:256]
    string_hmac_cipher = cut.decode()
    return string_hmac_cipher


def get_remotes_config() -> List[str]:
    cmd = f"git show git-annex:remote.log"
    return run_command(cmd).split("\n")


def lookup_download_decrypt(file_path: Path):
    destination_path = file_path.resolve()
    file_size = utils.get_file_size_from_key(lookup_key(file_path))
    if not utils.needs_download(destination_path, file_size):
        logger.info(f"Skipping already downloaded \n\t '{file_path}'.")
    else:
        enc_key = get_encrypted_key(file_path)
        logger.info(f"Downloading '{file_path}'...")
        download_from_s3(args.bucket, enc_key, args.prefix)
        utils.mkdirs(destination_path)
        decrypt_file(f"/tmp/{enc_key}", destination_path)
    logger.info(f"ok")
