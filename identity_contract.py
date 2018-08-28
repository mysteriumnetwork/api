from web3 import Web3, HTTPProvider
from abi import IDENTITY_CONTRACT_ABI


class IdentityContract:
    web3 = None
    contract = None

    def __init__(self, provider_endpoint_uri, contract_address):
        self.web3 = Web3(HTTPProvider(provider_endpoint_uri))

        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=IDENTITY_CONTRACT_ABI,
        )

    def is_registered(self, identity):
        checksum_address = self.web3.toChecksumAddress(identity)
        return self.contract.functions.isRegistered(checksum_address).call()


class IdentityContractFake:
    registered = None

    def __init__(self, registered):
        self.registered = registered

    def is_registered(self, identity):
        return self.registered
