# (c) 2024 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
"""Module to handle file transfer to a server.

This module allows to transfer files to and from a server

Examples
--------
>>> from ansys.api.speos import grpc_stub
>>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
>>> stub = grpc_stub.get_stub_insecure_channel(
    target="localhost:50051",
    stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
>>> from ansys.api.speos.file.v1 import file_transfer
>>> upload_response = file_transfer.upload_file(
        file_transfer_service_stub=stub,
        file_path="path/to/file")
>>> file_transfer.download_file(
            file_transfer_service_stub=stub,
            file_uri=upload_response.uri,
            download_location="path/to/download/location")
"""
import datetime
import os.path
import pathlib

import ansys.api.speos.file.v1.file_transfer_pb2 as file_transfer__v1__pb2
import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
import google.protobuf.duration_pb2 as duration_pb2


def file_to_chunks(file, chunk_size=4000000):
    """Cut a file into chunks of specified chunk_size.

    Parameters
    ----------
    file : file object
    chunk_size : size
        number of bytes max in the chunk - default to 4000000

    Examples
    --------
    >>> from ansys.api.speos.file.v1 import file_transfer
    >>> with open("path/to/file", "rb") as file:
    >>>     chunk_iterator = file_transfer.file_to_chunks(file=file)
    >>>     # do something with chunk iterator
    """
    while buffer := file.read(chunk_size):
        chunk = file_transfer__v1__pb2.Chunk(binary=buffer, size=len(buffer))
        yield chunk


def upload_file(
    file_transfer_service_stub: file_transfer__v1__pb2_grpc.FileTransferServiceStub,
    file_path: str,
    reserved_file_uri: str = "",
) -> file_transfer__v1__pb2.Upload_Response:
    """Upload a file to a server.

    Parameters
    ----------
    file_transfer_service_stub
        gRPC stub for file transfer service v1

    file_path
        file's path to be uploaded

    reserved_file_uri
        Optional - in case an uri was already reserved in server for the file.

    Returns
    -------
    Upload_Response - object created from file_transfer.proto file, response of Upload procedure
    contains for example file uri and upload duration

    Examples
    --------
    >>> from ansys.api.speos import grpc_stub
    >>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
    >>> stub = grpc_stub.get_stub_insecure_channel(
        target="localhost:50051",
        stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
    >>> from ansys.api.speos.file.v1 import file_transfer
    >>> file_transfer.upload_file(
            file_transfer_service_stub=stub,
            file_path="path/to/file")
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise ValueError("incorrect file_path : " + file_path)
    
    with open(file_path, "rb") as file:
        chunk_iterator = file_to_chunks(file)

        metadata = [("file-name", os.path.basename(file_path)), ("file-size", str(os.path.getsize(file_path)))]
        if reserved_file_uri:
            metadata.append(("reserved-file-uri", reserved_file_uri))
        upload_response = file_transfer_service_stub.Upload(chunk_iterator, metadata=metadata)

        return upload_response


def upload_folder(
    file_transfer_service_stub: file_transfer__v1__pb2_grpc.FileTransferServiceStub,
    folder_path: str,
    main_file_name: str,
    reserved_main_file_uri: str = "",
) -> [file_transfer__v1__pb2.Upload_Response]:
    """Upload several files to a server.

    Parameters
    ----------
    file_transfer_service_stub
        gRPC stub for file transfer service v1

    folder_path
        folder's path containing all files to upload

    main_file_name
        name of the file that will be considered as main - other files will be dependencies of main.

    reserved_main_file_uri
        Optional - in case an uri was already reserved in server for the main file.

    Returns
    -------
    List of Upload_Response - object created from file_transfer.proto file, response of Upload procedure
    contains for example file uri and upload duration

    Examples
    --------
    >>> from ansys.api.speos import grpc_stub
    >>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
    >>> stub = grpc_stub.get_stub_insecure_channel(
        target="localhost:50051",
        stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
    >>> from ansys.api.speos.file.v1 import file_transfer
    >>> file_transfer.upload_folder(
            file_transfer_service_stub=stub,
            folder_path="path/to/file"
            main_file_name="MainFileName.ext")
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise ValueError("incorrect folder_path : " + folder_path)

    main_file_path = os.path.join(folder_path, main_file_name)
    if not os.path.exists(main_file_path) or not os.path.isfile(main_file_path):
        raise ValueError("incorrect main_file_path : " + main_file_path)

    upload_responses = []
    add_dependencies_request = file_transfer__v1__pb2.AddDependencies_Request()
    # Upload all files, gather upload responses and use uri to fill request for dependencies call
    for file_to_upload in list(pathlib.Path(folder_path).glob("*")):
        if not os.path.isfile(file_to_upload):
            continue

        upload_response = file_transfer__v1__pb2.Upload_Response()
        if os.path.basename(file_to_upload) == os.path.basename(main_file_path):
            upload_response = upload_file(file_transfer_service_stub, file_to_upload, reserved_main_file_uri)
            add_dependencies_request.uri = upload_response.info.uri
        else:
            upload_response = upload_file(file_transfer_service_stub, file_to_upload)
            add_dependencies_request.dependency_uris.append(upload_response.info.uri)
        upload_responses.append(upload_response)

    # Send dependencies to server
    if len(add_dependencies_request.dependency_uris) > 0:
        file_transfer_service_stub.AddDependencies(add_dependencies_request)

    return upload_responses


def download_file(
    file_transfer_service_stub: file_transfer__v1__pb2_grpc.FileTransferServiceStub,
    file_uri: str,
    download_location: str,
) -> file_transfer__v1__pb2.Download_Response:
    """Download a file from a server.

    Parameters
    ----------
    file_transfer_service_stub
        gRPC stub for file transfer service v1

    file_uri
        file's uri on the server

    download_location
        path of download location

    Returns
    -------
    Download_Response - object created from file_transfer.proto file
    contains for example file uri, file name, file size and download duration

    Examples
    --------
    >>> from ansys.api.speos import grpc_stub
    >>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
    >>> stub = grpc_stub.get_stub_insecure_channel(
        target="localhost:50051",
        stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
    >>> from ansys.api.speos.file.v1 import file_transfer
    >>> file_transfer.download_file(
            file_transfer_service_stub=stub,
            file_uri="uri_file_to_download",
            download_location="path/to/download/location")
    """
    start_time = datetime.datetime.now()
    if not os.path.exists(download_location) or not os.path.isdir(download_location):
        raise ValueError("incorrect download_location : " + download_location)

    chunks = file_transfer_service_stub.Download(file_transfer__v1__pb2.Download_Request(uri=file_uri))
    server_initial_metadata = dict(chunks.initial_metadata())
    file_path = os.path.join(download_location, server_initial_metadata["file-name"])
    with open(file_path, "wb") as file:
        for chunk in chunks:
            file.write(chunk.binary)

    if int(server_initial_metadata["file-size"]) != os.path.getsize(file_path):
        raise ValueError("File download incomplete : " + file_path)

    # Compute download duration
    download_duration = datetime.datetime.now() - start_time

    # Fill response
    download_response = file_transfer__v1__pb2.Download_Response()
    download_response.info.uri = file_uri
    download_response.info.file_name = server_initial_metadata["file-name"]
    download_response.info.file_size = int(server_initial_metadata["file-size"])
    s = int(download_duration.total_seconds())
    download_response.download_duration.seconds = s
    ns = int(1000 * (download_duration - datetime.timedelta(seconds=s)) / datetime.timedelta(microseconds=1))
    download_response.download_duration.nanos = ns if ns != 0 else 1000
    return download_response


def download_folder(
    file_transfer_service_stub: file_transfer__v1__pb2_grpc.FileTransferServiceStub,
    main_file_uri: str,
    download_location: str,
) -> [file_transfer__v1__pb2.Download_Response]:
    """Download several files from a server.

    Parameters
    ----------
    file_transfer_service_stub
        gRPC stub for file transfer service v1

    main_file_uri : Str
        main file's uri on the server - this file and all its dependencies will be downloaded

    download_location : Path
        path of download location

    Returns
    -------
    List of Download_Response - object created from file_transfer.proto file
    contains for example file uri, file name, file size and download duration

    Examples
    --------
    >>> from ansys.api.speos import grpc_stub
    >>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
    >>> stub = grpc_stub.get_stub_insecure_channel(
        target="localhost:50051",
        stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
    >>> from ansys.api.speos.file.v1 import file_transfer
    >>> file_transfer.download_folder(
            file_transfer_service_stub=stub,
            main_file_uri="uri",
            download_location="path/to/download/location")
    """
    if not os.path.exists(download_location) or not os.path.isdir(download_location):
        raise ValueError("incorrect download_location : " + download_location)
    response = []

    # List all dependencies for the requested file
    list_deps_result = file_transfer_service_stub.ListDependencies(
        file_transfer__v1__pb2.ListDependencies_Request(uri=main_file_uri)
    )

    # Download first the main file
    response.append(download_file(file_transfer_service_stub, main_file_uri, download_location))

    # Then its dependencies
    for dep in list_deps_result.dependency_infos:
        response.append(download_file(file_transfer_service_stub, dep.uri, download_location))

    if not response:
        raise ValueError("no files downloaded for mainFileUri : " + main_file_uri)

    return response
