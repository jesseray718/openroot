# Identity Analysis — Cycle-004

## Key sections extracted 20260813T071409Z
36:import hashlib
45:class Identity:
47:    This class is used to manage identities in Reticulum. It provides methods
86:    Constant specifying the truncated hash length (in bits) used by Reticulum
87:    for addressable hashes and other purposes. Non-configurable.
97:    ratchet_persist_lock = threading.Lock()
101:    def remember(packet_hash, destination_hash, public_key, app_data = None):
103:            raise TypeError("Can't remember "+RNS.prettyhexrep(destination_hash)+", the public key size of "+str(len(public_key))+" is not valid.", RNS.LOG_ERROR)
106:                if not destination_hash in Identity.known_destinations:
107:                    Identity.known_destinations[destination_hash] = [time.time(), packet_hash, public_key, app_data, 0]
109:                    entry = Identity.known_destinations[destination_hash]
111:                    entry[1] = packet_hash
116:    def recall(target_hash, from_identity_hash=False, _no_use=False):
118:        Recall identity for a destination or identity hash. By default, this function
119:        will return the identity associated with a given *destination* hash. As an
120:        example, if you know the ``lxmf.delivery`` destination hash of an endpoint,
122:        search for an identity from a known *identity hash*, by setting the
123:        ``from_identity_hash`` argument.
125:        :param target_hash: Destination or identity hash as *bytes*.
126:        :param from_identity_hash: Whether to search based on identity hash instead of destination hash as *bool*.
129:        if from_identity_hash:
130:            with Identity.known_destinations_lock: destination_hashes = list(Identity.known_destinations.keys())
131:            for destination_hash in destination_hashes:
132:                entry = Identity.known_destinations.get(destination_hash)
134:                if target_hash == Identity.truncated_hash(entry[2]):
135:                    if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(destination_hash)
144:            if target_hash in Identity.known_destinations:
145:                if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(target_hash)
146:                identity_data = Identity.known_destinations[target_hash]
153:                    if target_hash == registered_destination.hash:
162:    def recall_app_data(destination_hash, _no_use=False):
164:        Recall last heard app_data for a destination hash.
166:        :param destination_hash: Destination hash as *bytes*.
169:        if destination_hash in Identity.known_destinations:
170:            if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(destination_hash)
171:            app_data = Identity.known_destinations[destination_hash][3]
177:    def save_known_destinations(background=False, recombine=False):
178:        if recombine: RNS.log(f"Recombining known destinations from disk cache on persist is deprecated, argument ignored", RNS.LOG_WARNING)
216:    def load_known_destinations():
242:    def _used_destination_data(destination_hash):

## Full class + init + key methods
# Reticulum License
#
# Copyright (c) 2016-2025 Mark Qvist
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# - The Software shall not be used in any kind of system which includes amongst
#   its functions the ability to purposefully do harm to human beings.
#
# - The Software shall not be used, directly or indirectly, in the creation of
#   an artificial intelligence, machine learning or language model training
#   dataset, including but not limited to any use that contributes to the
#   training or development of such a model or algorithm.
#
# - The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import os
import RNS
import time
import atexit
import hashlib
import threading

from .vendor import umsgpack as umsgpack

from RNS.Cryptography import X25519PrivateKey, X25519PublicKey, Ed25519PrivateKey, Ed25519PublicKey
from RNS.Cryptography import Token


class Identity:
    """
    This class is used to manage identities in Reticulum. It provides methods
    for encryption, decryption, signatures and verification, and is the basis
    for all encrypted communication over Reticulum networks.

    :param create_keys: Specifies whether new encryption and signing keys should be generated.
    """

    CURVE = "Curve25519"
    """
    The curve used for Elliptic Curve DH key exchanges
    """

    KEYSIZE     = 256*2
    """
    X.25519 key size in bits. A complete key is the concatenation of a 256 bit encryption key, and a 256 bit signing key.
    """

    RATCHETSIZE = 256
    """
    X.25519 ratchet key size in bits.
    """

    RATCHET_EXPIRY = 60*60*24*30
    """
    The expiry time for received ratchets in seconds, defaults to 30 days. Reticulum will always use the most recently
    announced ratchet, and remember it for up to ``RATCHET_EXPIRY`` since receiving it, after which it will be discarded.
    If a newer ratchet is announced in the meantime, it will be replace the already known ratchet.
    """

    # Non-configurable constants
    TOKEN_OVERHEAD            = RNS.Cryptography.Token.TOKEN_OVERHEAD
    AES128_BLOCKSIZE          = 16          # In bytes
    AES256_BLOCKSIZE          = 16          # In bytes
    HASHLENGTH                = 256         # In bits
    SIGLENGTH                 = KEYSIZE     # In bits

    NAME_HASH_LENGTH          = 80
    TRUNCATED_HASHLENGTH      = RNS.Reticulum.TRUNCATED_HASHLENGTH
    """
    Constant specifying the truncated hash length (in bits) used by Reticulum
    for addressable hashes and other purposes. Non-configurable.
    """

    DERIVED_KEY_LENGTH        = 512//8
    DERIVED_KEY_LENGTH_LEGACY = 256//8

    # Storage
    known_destinations = {}
    known_ratchets = {}

    ratchet_persist_lock = threading.Lock()
    known_destinations_lock = threading.Lock()

    @staticmethod
    def remember(packet_hash, destination_hash, public_key, app_data = None):
        if len(public_key) != Identity.KEYSIZE//8:
            raise TypeError("Can't remember "+RNS.prettyhexrep(destination_hash)+", the public key size of "+str(len(public_key))+" is not valid.", RNS.LOG_ERROR)
        else:
            with Identity.known_destinations_lock:
                if not destination_hash in Identity.known_destinations:
                    Identity.known_destinations[destination_hash] = [time.time(), packet_hash, public_key, app_data, 0]
                else:
                    entry = Identity.known_destinations[destination_hash]
                    entry[0] = time.time()
                    entry[1] = packet_hash
                    entry[2] = public_key
                    entry[3] = app_data

    @staticmethod
    def recall(target_hash, from_identity_hash=False, _no_use=False):
        """
        Recall identity for a destination or identity hash. By default, this function
        will return the identity associated with a given *destination* hash. As an
        example, if you know the ``lxmf.delivery`` destination hash of an endpoint,
        this function will return the associated underlying identity. You can also
        search for an identity from a known *identity hash*, by setting the
        ``from_identity_hash`` argument.

        :param target_hash: Destination or identity hash as *bytes*.
        :param from_identity_hash: Whether to search based on identity hash instead of destination hash as *bool*.
        :returns: An :ref:`RNS.Identity<api-identity>` instance that can be used to create an outgoing :ref:`RNS.Destination<api-destination>`, or *None* if the destination is unknown.
        """
        if from_identity_hash:
            with Identity.known_destinations_lock: destination_hashes = list(Identity.known_destinations.keys())
            for destination_hash in destination_hashes:
                entry = Identity.known_destinations.get(destination_hash)
                if not entry: continue
                if target_hash == Identity.truncated_hash(entry[2]):
                    if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(destination_hash)
                    identity = Identity(create_keys=False)
                    identity.load_public_key(entry[2])
                    identity.app_data = entry[3]
                    return identity

            return None

        else:
            if target_hash in Identity.known_destinations:
                if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(target_hash)
                identity_data = Identity.known_destinations[target_hash]
                identity = Identity(create_keys=False)
                identity.load_public_key(identity_data[2])
                identity.app_data = identity_data[3]
                return identity
            else:
                for registered_destination in RNS.Transport.destinations:
                    if target_hash == registered_destination.hash:
                        identity = Identity(create_keys=False)
                        identity.load_public_key(registered_destination.identity.get_public_key())
                        identity.app_data = None
                        return identity

                return None

    @staticmethod
    def recall_app_data(destination_hash, _no_use=False):
        """
        Recall last heard app_data for a destination hash.

        :param destination_hash: Destination hash as *bytes*.
        :returns: *Bytes* containing app_data, or *None* if the destination is unknown.
        """
        if destination_hash in Identity.known_destinations:
            if not _no_use: RNS.Reticulum.get_instance()._used_destination_data(destination_hash)
            app_data = Identity.known_destinations[destination_hash][3]
            return app_data
        
        else: return None

    @staticmethod
    def save_known_destinations(background=False, recombine=False):
        if recombine: RNS.log(f"Recombining known destinations from disk cache on persist is deprecated, argument ignored", RNS.LOG_WARNING)
        if RNS.Transport.owner.is_connected_to_shared_instance: return
        
