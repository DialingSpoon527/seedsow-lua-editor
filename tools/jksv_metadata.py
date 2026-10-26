"""Generate portable JKSV revision-1 metadata for an explicit account-save target.

No game or region is assumed. This describes a target; it does not convert game
save contents or establish that another edition can load them.
Layout: https://github.com/J-D-K/JKSV/blob/rewrite/include/fs/SaveMetaData.hpp
"""
import struct


def portable_account_metadata(application_id, *, owner_id, data_size, journal_size):
    """Standard account save (type/space 1, rank/index/flags 0), no personal data.

    Get both IDs and sizes from the intended title's own JKSV backup metadata.
    Nonstandard save attributes require separate review; they are not inferred.
    """
    for name, value in (('application_id', application_id), ('owner_id', owner_id)):
        if type(value) is not int or not 0 < value < 2**64:
            raise ValueError(name+' must be a nonzero unsigned 64-bit integer.')
    for name, value in (('data_size', data_size), ('journal_size', journal_size)):
        if type(value) is not int or not 0 <= value < 2**63:
            raise ValueError(name+' must be a nonnegative signed 64-bit integer.')
    if data_size == 0:
        raise ValueError('data_size must be positive.')
    return struct.pack('<IBQ16sQBBHQQIqqQB', 0x56534B4A, 1, application_id,
                       bytes(16), 0, 1, 0, 0, owner_id, 0, 0,
                       data_size, journal_size, 0, 1)
