# ===================================================================
#
# Copyright (c) 2014, Legrandin <helderijs@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===================================================================

"""
MD2 cryptographic hash algorithm.

MD2 is specified in RFC1319_ and it produces the 128 bit digest of a message.

    >>> from Cryptodome.Hash import MD2
    >>>
    >>> h = MD2.new()
    >>> h.update(b'Hello')
    >>> print h.hexdigest()

MD2 stand for Message Digest version 2, and it was invented by Rivest in 1989.
This algorithm is both slow and insecure. Do not use it for new designs.

.. _RFC1319: http://tools.ietf.org/html/rfc1319
"""

from Cryptodome.Util.py3compat import bord

from Cryptodome.Util._raw_api import (load_pycryptodome_raw_lib,
                                  VoidPointer, SmartPointer,
                                  create_string_buffer,
                                  get_raw_buffer, c_size_t,
                                  expect_byte_string)

_raw_md2_lib = load_pycryptodome_raw_lib(
                        "Cryptodome.Hash._MD2",
                        """
                        int md2_init(void **shaState);
                        int md2_destroy(void *shaState);
                        int md2_update(void *hs,
                                          const uint8_t *buf,
                                          size_t len);
                        int md2_digest(const void *shaState,
                                          uint8_t digest[20]);
                        int md2_copy(const void *src, void *dst);
                        """)


class MD2Hash(object):
    """Class that implements an MD2 hash
    """

    #: The size of the resulting hash in bytes.
    digest_size = 16
    #: The internal block size of the hash algorithm in bytes.
    block_size = 64
    #: ASN.1 Object ID
    oid = "1.2.840.113549.2.2"

    def __init__(self, data=None):
        state = VoidPointer()
        result = _raw_md2_lib.md2_init(state.address_of())
        if result:
            raise ValueError("Error %d while instantiating MD2"
                             % result)
        self._state = SmartPointer(state.get(),
                                   _raw_md2_lib.md2_destroy)
        if data:
            self.update(data)

    def update(self, data):
        """Continue hashing of a message by consuming the next chunk of data.

        Repeated calls are equivalent to a single call with the concatenation
        of all the arguments. In other words:

           >>> m.update(a); m.update(b)

        is equivalent to:

           >>> m.update(a+b)

        :Parameters:
          data : byte string
            The next chunk of the message being hashed.
        """

        expect_byte_string(data)
        result = _raw_md2_lib.md2_update(self._state.get(),
                                         data,
                                         c_size_t(len(data)))
        if result:
            raise ValueError("Error %d while instantiating MD2"
                             % result)

    def digest(self):
        """Return the **binary** (non-printable) digest of the message that
        has been hashed so far.

        This method does not change the state of the hash object.
        You can continue updating the object after calling this function.

        :Return: A byte string of `digest_size` bytes. It may contain non-ASCII
         characters, including null bytes.
        """

        bfr = create_string_buffer(self.digest_size)
        result = _raw_md2_lib.md2_digest(self._state.get(),
                                         bfr)
        if result:
            raise ValueError("Error %d while instantiating MD2"
                             % result)

        return get_raw_buffer(bfr)

    def hexdigest(self):
        """Return the **printable** digest of the message that has been
        hashed so far.

        This method does not change the state of the hash object.

        :Return: A string of 2* `digest_size` characters. It contains only
         hexadecimal ASCII digits.
        """

        return "".join(["%02x" % bord(x) for x in self.digest()])

    def copy(self):
        """Return a copy ("clone") of the hash object.

        The copy will have the same internal state as the original hash
        object.
        This can be used to efficiently compute the digests of strings that
        share a common initial substring.

        :Return: A hash object of the same type
        """

        clone = MD2Hash()
        result = _raw_md2_lib.md2_copy(self._state.get(),
                                       clone._state.get())
        if result:
            raise ValueError("Error %d while copying MD2" % result)
        return clone

    def new(self, data=None):
        return MD2Hash(data)


def new(data=None):
    """Return a fresh instance of the hash object.

    :Parameters:
       data : byte string
        The very first chunk of the message to hash.
        It is equivalent to an early call to `MD2Hash.update()`.
        Optional.

    :Return: A `MD2Hash` object
    """
    return MD2Hash().new(data)

#: The size of the resulting hash in bytes.
digest_size = MD2Hash.digest_size

#: The internal block size of the hash algorithm in bytes.
block_size = MD2Hash.block_size
