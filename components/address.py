# Standard Library
import hashlib
# Third-Party
import ecdsa
import base58
# Helpers
from components import static
# Project

class Address:
    def __init__(self, private_key=None):
        self.signing_key, self.private_key = None, None
        self.verifying_key, self.public_key = None, None
        self.address, self.balance = None, None

        if private_key is not None:
            self.import_address(private_key)
        else:
            self.new_address()

    def __repr__(self):
        return self.address

    def new_address(self):
        self.signing_key = ecdsa.SigningKey.generate()
        self.verifying_key = self.signing_key.get_verifying_key()
        self.__generate_private_and_public_keys()
        self.address = self.generate_address()
        self.__acquire_balance()

    def import_address(self, pk):
        self.signing_key = ecdsa.SigningKey.from_string(pk)
        self.verifying_key = self.signing_key.get_verifying_key()
        self.__generate_private_and_public_keys()
        self.address = self.generate_address()
        self.__acquire_balance()

    def __generate_private_and_public_keys(self):
        self.private_key = self.signing_key.to_string().hex()
        self.public_key = self.verifying_key.to_string().hex()


    def generate_address(self):
        # 0 - Having a private ECDSA key (assume that's how you got the public_key)

        # 1 - Take the corresponding public key generated with it (65 bytes, 1 byte 0x04, 32 bytes corresponding to X coordinate, 32 bytes corresponding to Y coordinate)
        step_1 = bytes(self.public_key, 'UTF-8')

        # 2 - Perform SHA-256 hashing on the public key
        step_2 = hashlib.sha256(step_1).digest()

        # 3 - Perform RIPEMD-160 hashing on the result of SHA-256
        h = hashlib.new('ripemd160')
        h.update(step_2)
        step_3 = h.digest()

        # 4 - Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
        step_4 = static.VERSION + step_3

        # 5 - Perform SHA-256 hash on the extended RIPEMD-160 result
        step_5 = hashlib.sha256(step_4)

        # 6 - Perform SHA-256 hash on the result of the previous SHA-256 hash
        step_6 = hashlib.sha256(step_5.digest())

        # 7 - Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
        step_7 = step_6.digest()[:8]

        # 8 - Add the 4 checksum bytes from stage 7 at the end of extended RIPEMD-160 hash from stage 4. This is the 25-byte binary Bitcoin Address.
        step_8 = step_4 + step_7

        # 9 - Convert the result from a byte string into a base58 string using Base58Check encoding. This is the most commonly used Bitcoin Address format
        step_9 = base58.b58encode_check(step_8)
        return step_9

    def __acquire_balance(self):
        # TODO
        if self.address is not None:
            self.balance = 0
        else:
            raise NotImplementedError("A balance cannot be acquired without a valid address.")

    def export_address(self):
        return {
            'sk': self.signing_key.to_string(),
            'vk': self.verifying_key.to_string()
        }

    def readable(self):
        return {
            "private": self.private_key,
            "public": self.public_key,
            "balance": self.balance,
            'address': self.address,
        }

if __name__ == "__main__":
    from pprint import pprint
    address = Address()
    address.new_address()

    address2 = Address()
    address2.import_address(address.export_address()['sk'])

    print(address.export_address())
    pprint(address.readable())
    pprint(address2.readable())
