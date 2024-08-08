# (c) 2024 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
"""Module to handle gRPC stub.

This module allows to get gRPC stub

Examples
--------
>>> from ansys.api.speos import grpc_stub
>>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
>>> grpc_stub.get_stub_insecure_channel(
        target="localhost:50051",
        stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub)
"""
import grpc


def get_stub_insecure_channel(target, stub_type, options=[]):
    """Get gRPC stub with insecure channel.

    Parameters
    ----------
    target : the server address
    stub_type : type
        type of the stub which will be returned.
    options : optional - options list that will be forwarded to grpc.insecure_channel

    Returns
    -------
    stub_type
        gRPC stub.

    Examples
    --------
    >>> from ansys.api.speos import grpc_stub
    >>> import ansys.api.speos.file.v1.file_transfer_pb2_grpc as file_transfer__v1__pb2_grpc
    >>> grpc_stub.get_stub_insecure_channel(
            target="localhost:50051",
            stub_type=file_transfer__v1__pb2_grpc.FileTransferServiceStub,
            options=[('grpc.max_receive_message_length', 1024 * 1024 * 1024),])
    """
    channel = grpc.insecure_channel(target, options)
    return stub_type(channel)
