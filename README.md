
# Garlic Crypt 🧄
Soft privacy for public ledgers

Garlic Crypt sweeps or splits Ethereum accounts, providing a privacy layer by momentarily trusting an offchain signing server.
Funds are custodied onchain and the receipt provided by the signkng server verifiably grants access to the custodied funds.

Receipts should never be cashed in immediately, since it would make a timing attack trivial.
Signing server should always involve either splitting or joining to prevent transactions from being deanonymised by comparing tx amount.



