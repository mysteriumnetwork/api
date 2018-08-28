IDENTITY_CONTRACT_ABI = [{
    "constant": True,
    "inputs": [],
    "name": "registrationFee",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": True,
    "inputs": [{"name": "", "type": "address"}],
    "name": "balances",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "receiverAndSigns", "type": "bytes32"}, {
        "name": "extraDataHash",
        "type": "bytes32"
    }, {"name": "seq", "type": "uint256"}, {"name": "amount", "type": "uint256"}, {
                   "name": "sender_R",
                   "type": "bytes32"
               }, {"name": "sender_S", "type": "bytes32"}, {"name": "receiver_R", "type": "bytes32"}, {
                   "name": "receiver_S",
                   "type": "bytes32"
               }],
    "name": "clearPromise",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "newFee", "type": "uint256"}],
    "name": "changeRegistrationFee",
    "outputs": [],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "amount", "type": "uint256"}, {"name": "v", "type": "uint8"}, {
        "name": "r",
        "type": "bytes32"
    }, {"name": "s", "type": "bytes32"}],
    "name": "withdraw",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "ERC20Token",
    "outputs": [{"name": "", "type": "address"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": True,
    "inputs": [{"name": "identity", "type": "address"}],
    "name": "getPublicKey",
    "outputs": [{"name": "", "type": "bytes32"}, {"name": "", "type": "bytes32"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "owner",
    "outputs": [{"name": "", "type": "address"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "pubKeyPart1", "type": "bytes32"}, {"name": "pubKeyPart2", "type": "bytes32"}, {
        "name": "v",
        "type": "uint8"
    }, {"name": "r", "type": "bytes32"}, {"name": "s", "type": "bytes32"}],
    "name": "RegisterIdentity",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": True,
    "inputs": [{"name": "identity", "type": "address"}],
    "name": "isRegistered",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "identity", "type": "address"}, {"name": "amount", "type": "uint256"}],
    "name": "topUp",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "receiver", "type": "address"}],
    "name": "transferCollectedFeeTo",
    "outputs": [{"name": "", "type": "bool"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "collectedFee",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "constant": False,
    "inputs": [{"name": "newOwner", "type": "address"}],
    "name": "transferOwnership",
    "outputs": [],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "constant": True,
    "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
    "name": "clearedPromises",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{"name": "erc20address", "type": "address"}, {"name": "registrationFee", "type": "uint256"}],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "constructor"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "from", "type": "address"}, {
        "indexed": True,
        "name": "to",
        "type": "address"
    }, {"indexed": False, "name": "seqNo", "type": "uint256"}, {"indexed": False, "name": "amount", "type": "uint256"}],
    "name": "PromiseCleared",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "identity", "type": "address"}, {
        "indexed": False,
        "name": "amount",
        "type": "uint256"
    }, {"indexed": False, "name": "totalBalance", "type": "uint256"}],
    "name": "ToppedUp",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "identity", "type": "address"}, {
        "indexed": False,
        "name": "amount",
        "type": "uint256"
    }, {"indexed": False, "name": "totalBalance", "type": "uint256"}],
    "name": "Withdrawn",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "identity", "type": "address"}],
    "name": "Registered",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "name": "previousOwner", "type": "address"}, {
        "indexed": True,
        "name": "newOwner",
        "type": "address"
    }],
    "name": "OwnershipTransferred",
    "type": "event"
}]
