// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;
// import from github if you can... e.g. 
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.7.3/ownership/Ownable.sol";
// but if using hardhat, yopu'll need to npm it:
import "@openzeppelin/contracts/access/Ownable.sol";
// Uncomment this line to use console.log
import "hardhat/console.sol";

contract Garlique is Ownable {
    string constant VERSION = "0.1";
    // string constant  = "";
    // string constant  = "";
    // string constant  = "";

    enum address_type {
        EXTERNAL,               // Externally-owned acount
        EXTERNAL_GASLESS,       // EIP-4337 or address with isValidSignature()
        INTERNAL                // Offchain address - May not be H160 format
    }
    
    enum receiver_type {
        EXTERNAL,               
        EXTERNAL_GASLESS,
        INTERNAL,
        FEE,                    // Stored in this contract's balance, not in state, administered by admin role
        DONATE                  // Stored in this contract's balance, in dao_balance, administered by governance (DAO-like)
    }

    // Example staking/ yield custody contract addresses. 
    // Currently, these hardcoded examples would allow instant unstaking. 
    // We can use cheque.redeemFromUnixTime to schedule the server to unstake early. Future work ;)
    enum custodian {
        GARLIQUE,
        LIDO_STETH,
        WSHIBU_PONZI_LP
    }

    struct SignedCheque {
        uint value;                     // 32 byte
        uint redeemFromUnixTime;        // 32 byte out of sympathy for solidity, but only needs to be 4 byte
        address payable rcvr;           // 20 byte
        receiver_type rcvr_type;        // 1 byte
        custodian custody_option;       // 1 byte
        bytes4 salt;                    // 4 byte
        uint8 v;                        // 1 byte
        bytes32 r;                      // 32 byte
        bytes32 s;                      // 32 byte
        bytes32 msgHash;                // 32 byte
    }

    // address payable public owner;
    uint public dao_balance;
    address public garlic_patch;                                // signing server address to ecrecover

    mapping(address=> bool) public old_garlic_patches;          // maintain compatibility with previous signers, subject to admin release

    mapping(uint => bool) public spent;  

    mapping(custodian => address) public custodians;


    event Deposit(uint amount, address owner, uint block);

    event Spent(uint txSig, uint amount, address receiver, uint block);

    event OfflineSignerChanged(address oldSigner, address newSigner, uint block);

    constructor(address _garlic_patch) payable {

        // owner = payable(msg.sender);
        garlic_patch = _garlic_patch;

        custodians[custodian.LIDO_STETH]=0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84;
        custodians[custodian.WSHIBU_PONZI_LP]=0xd2877702675e6cEb975b4A1dFf9fb7BAF4C91ea9;
    }

    receive() external payable {
        require (tx.origin==msg.sender, "Contracts may not fund this contract yet. We haven't implemented attributing the funds to the rightful owner.");
        emit Deposit(msg.value, msg.sender, block.number);
    }

    function updateGarlicPatch(address _newGarlicPatch) public onlyOwner() returns (bool) {
        old_garlic_patches[garlic_patch] = true;
        emit OfflineSignerChanged(garlic_patch, _newGarlicPatch, block.number);
        garlic_patch = _newGarlicPatch;
        return true;
    }

    // Prefix string!


    // Expects hash as per using web3.py :
    // from web3 import Web3
    // from eth_account.messages import encode_defunct, _hash_eip191_message
    // message = value32b,redeemFromUnixTime32b, rcvr20b ,rcvr_type1b {0..4}, custody_option1b {0..}, salt4b
    // message_hash = _hash_eip191_message(message)
    function verifyChequeHash(SignedCheque calldata _cheque) internal returns (bool) {        
        bytes32 actualHash =  keccak256(abi.encodePacked(
            _cheque.value, _cheque.redeemFromUnixTime, _cheque.rcvr, _cheque.rcvr_type, _cheque.custody_option, _cheque.salt
        ));
        require (_cheque.msgHash == actualHash);
        return true;
    }


    // https://web3py.readthedocs.io/en/latest/web3.eth.account.html#sign-a-message
    // from web3.auto import w3
    // (r, s, v) = w3.eth.account.sign_message(message_hash, private_key)
    function verifySignedCheque(SignedCheque calldata _cheque) internal returns (bool) {
        require (verifyChequeHash(_cheque), "Cheque details have been tampered.");
        // TODO - check that ecrecover works as expected on every chain..

        address signer;
        bytes32 msgHash = _cheque.msgHash;
        uint8 v = _cheque.v;
        bytes32 r = _cheque.r;
        bytes32 s = _cheque.s;
        
        signer = ecrecover(msgHash, v, r, s);

        require(_cheque.rcvr==signer, "Cheque signed by bad signer");

        return false;

    }

    // from web3 import Web3
    // from eth_account.messages import _hash_eip191_message
    // message_hash = _hash_eip191_message(_newReceiver)
    function verifyEOASigned(address _oldReceiver, address _newReceiver, bytes32 r, bytes32 s, uint8 v) public returns (bool) {
        // TODO - change testing visibility (to internal)

        require(hasDeployedContract(_oldReceiver));
        // TODO: Implement EIP 1271 check
        
        bytes32 msgHash = keccak256(abi.encodePacked(_newReceiver));
        address signer = ecrecover(msgHash, v, r, s);

        EIP4337Sig = (v,r,s)
        _oldReceiver.isValidSignature(hash, signature) 
        require (_oldReceiver==signer, "Payment to receiver address must pass isValidSignature() of original receiver.");
        
        return true;
    }

    // TODO - change testing visibility (to internal)
    function verifyGaslessSigned(address _oldReceiver, address _newReceiver, bytes32 r, bytes32 s, uint8 v) public returns (bool) {

        bytes32 msgHash = keccak256(abi.encodePacked(_newReceiver));
        address signer = ecrecover(msgHash, v, r, s);
        require (_oldReceiver==signer, "Payment to receiver address must be signed by original receiver.");
        
        return true;
    }

    function _spendChequeTo(SignedCheque calldata _cheque, address payable _receiver) internal returns (bool) {
        // You should perform require(receiver_type == ...) before calling _spendChequeTo.
        require(block.timestamp>=_cheque.redeemFromUnixTime, "Cheque cannot be redeemed before "); // TODO: +_cheque.redeemFromUnixTime);

        receiver_type rcvr_type = _cheque.rcvr_type;
        // address payable receiver = _receiver;
        uint amount = _cheque.value;
        bool success;

        if (rcvr_type==receiver_type.EXTERNAL) {
            (success, )= _receiver.call{value: amount}("");
        } else
        if (rcvr_type==receiver_type.EXTERNAL_GASLESS) {
            (success, )= _receiver.call{value: amount}("");
        } else
        if (rcvr_type==receiver_type.INTERNAL) {
            revert ("Error: not implemented. You should not have reached here");
        } else
        if (rcvr_type==receiver_type.FEE) {
            // console.log ('Nyum')
        } else
        if (rcvr_type==receiver_type.DONATE) {
            dao_balance += amount;
            // console.log ('Thxxx 🥰🥰🥰')
        } else
        { 
            revert ("unknown receiver type "); // TODO: ++_cheque.rcvr_type);
        }
        
        spent[_cheque.signature] = true;
        emit Spent(_cheque.signature, amount, _receiver, block.number);
        success = pullCustodiedFunds(custodians[_cheque.custody_option], amount);
        return success;

    }

    // Placeholder before implementing EIP1271 check.. 
    // Not technically isContract(), since a CREATE2 contract not yet deployed would show as EOA. 
    // But re-entrancy is prevented by Checks-Effects-Interactions
    function hasDeployedContract(address isItContract) returns (bool) {
        return isItContract.code.size >0;            
    }


    function pullCustodiedFunds(address _custodian, uint _amount) internal returns (bool) {
        // Not implemented 🤷🏻‍♀
        return true;
    }

    function spendOneCheque(SignedCheque calldata _cheque) public returns (bool) {
        bool success;
        if (_cheque.rcvr_type == receiver_type.EXTERNAL) {
            success = spendOneEOAChequeToSelf(_cheque);
        } else
        if (_cheque.rcvr_type == receiver_type.EXTERNAL_GASLESS) {
            success = spendOneGaslessChequeToSelf(_cheque);
            
        } else
        if (_cheque.rcvr_type == receiver_type.INTERNAL) {
            // Not implemented - will revert.
            success = spendOneToInternal(_cheque);
            
        } else
        if (_cheque.rcvr_type == receiver_type.FEE) {
            success = spendOneToThis(_cheque);
            
        } else
        if (_cheque.rcvr_type == receiver_type.DONATE) {
            success = spendOneToThis(_cheque);
            
        } else 
        { 
            revert ("unknown receiver type "); // TODO: ++_cheque.rcvr_type);
        }

        return success;
    }

    function spendOneEOAChequeToSelf(SignedCheque calldata _cheque) public returns (bool) {
        require (_cheque.rcvr_type == receiver_type.EXTERNAL, "Wrong method for receiver type "); // TODO: ++_cheque.rcvr_type);
        require (tx.origin==msg.sender, "Contract addresses (eg Safe/ EIP4337), use spendOneGaslessChequeToSelf.");
        require (_cheque.rcvr==msg.sender, "Spending to different address, use spendOneEOAChequeToOther.");
        require (verifySignedCheque(_cheque), "Bad signature.");
        return _spendChequeTo (_cheque, _cheque.rcvr);
    }

    function spendOneGaslessChequeToSelf(SignedCheque calldata _cheque) public returns (bool) {
        require (_cheque.rcvr_type == receiver_type.EXTERNAL_GASLESS, "Wrong method for receiver type "); // TODO: ++_cheque.rcvr_type);
        require (_cheque.rcvr==msg.sender, "Spending to different address, use spendOneGaslessChequeToOther.");
        require (verifySignedCheque(_cheque), "Bad signature.");
        return _spendChequeTo (_cheque, _cheque.rcvr);
    }

    function spendOneEOAChequeToOther(SignedCheque calldata _cheque, address payable _newReceiver, uint _signedNewReceiver) public returns (bool) {
        require (_cheque.rcvr_type == receiver_type.EXTERNAL, "Wrong method for receiver type "); // TODO: ++_cheque.rcvr_type);
        require (verifyEOASigned(_cheque.rcvr, _newReceiver, _signedNewReceiver), "Bad signature approving different receiver");
        require (verifySignedCheque(_cheque), "Bad signature.");
        return _spendChequeTo (_cheque, _newReceiver);
    }

    function spendOneGaslessChequeToOther(SignedCheque calldata _cheque, address payable _newReceiver, uint _signedNewReceiver) public returns (bool) {
        require (_cheque.rcvr_type == receiver_type.EXTERNAL_GASLESS, "Wrong method for receiver type "); // TODO: ++_cheque.rcvr_type);
        require (verifyGaslessSigned(_cheque.rcvr, _newReceiver, _signedNewReceiver), "Bad signature approving different receiver");
        require (verifySignedCheque(_cheque), "Bad signature.");
        return _spendChequeTo (_cheque, _newReceiver);
    }

    function spendOneToInternal(SignedCheque calldata _cheque) public returns (bool)  {
        require (_cheque.rcvr_type == receiver_type.INTERNAL, "");
        require (false, "Internal cheques must be generated offchain. Send funds to this contract address to  ");
        return false;
    }

    function spendOneToThis(SignedCheque calldata _cheque) public returns (bool) {
        require (_cheque.rcvr_type == receiver_type.FEE || _cheque.rcvr_type == receiver_type.DONATE, "Wrong method for receiver type "); // TODO: ++_cheque.rcvr_type);
        return verifySignedCheque(_cheque);
    }


    function logChequeData (SignedCheque calldata _cheque) public {
        
    }

    function logVerifyChequeSig (SignedCheque calldata _cheque) public {

    }

}
