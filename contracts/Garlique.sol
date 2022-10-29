// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

// Uncomment this line to use console.log
import "hardhat/console.sol";

contract Garlique {
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
        address payable rcvr;           // 32 byte
        receiver_type rcvr_type;        // 1 byte
        custodian custody_option;       // 1 byte
        bytes12 salt;                   // 12 byte
        uint redeemFromUnixTime;        // 32 byte out of sympathy for solidity, but only needs to be 4 byte
        uint signature;                 // 32 byte
    }

    address payable public owner;
    uint public dao_balance;

    mapping(uint => bool) public spent;  

    mapping(custodian => address) public custodians;


    event Deposit(uint amount, address owner, uint when);

    event Spent(uint amount, address receiver, uint when);

    constructor() payable {
        owner = payable(msg.sender);

        custodians[custodian.LIDO_STETH]=0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84;
        custodians[custodian.WSHIBU_PONZI_LP]=0xd2877702675e6cEb975b4A1dFf9fb7BAF4C91ea9;
    }

    receive() external payable {
        require (tx.origin==msg.sender, "Contracts may not fund this contract yet. We haven't implemented attributing the funds to the rightful owner.");
        emit Deposit(msg.value, msg.sender, block.number);
    }

    function verifySignedCheque(SignedCheque calldata _cheque) internal returns (bool) {

        // TODO  - verify the damn sig!
        return false;

    }

    // TODO - change testing visibility (to internal)
    function verifyEOASigned(address _oldReceiver, address _newReceiver, uint _signedNewReceiver) public returns (bool) {

        // TODO  - verify the damn sig!
        return false;
    }

    // TODO - change testing visibility (to internal)
    function verifyGaslessSigned(address _oldReceiver, address _newReceiver, uint _signedNewReceiver) public returns (bool) {

        // TODO  - verify the damn sig!
        return false;
    }

    function _spendChequeTo(SignedCheque calldata _cheque, address payable _receiver) internal returns (bool) {
        // You should perform require(receiver_type == ...) before calling _spendChequeTo.
        require(block.timestamp>=_cheque.redeemFromUnixTime, "Cheque cannot be redeemed before "); // TODO: +_cheque.redeemFromUnixTime);

        receiver_type rcvr_type = _cheque.rcvr_type;
        uint amount = _cheque.value;
        bool success;

        if (rcvr_type==receiver_type.EXTERNAL) {
            // TODO send amount to _receiver
        }
        if (rcvr_type==receiver_type.EXTERNAL_GASLESS) {
            // TODO send amount to _receiver
        }
        if (rcvr_type==receiver_type.INTERNAL) {
            revert ("Error: not implemented. You should not have reached here");
        }
        if (rcvr_type==receiver_type.FEE) {
            // console.log ('Nyum')
        }
        if (rcvr_type==receiver_type.DONATE) {
            dao_balance += amount;
            // console.log ('Thxxx 🥰🥰🥰')
        }
        
        spent[_cheque.signature] = true;
        emit Spent(amount, _receiver, block.number);
        success = pullCustodiedFunds(custodians[_cheque.custody_option], amount);
        return success;

    }

    function pullCustodiedFunds (address _custodian, uint _amount) internal returns (bool) {
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
