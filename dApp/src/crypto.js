////////////// CONNECT //////////////

////////////// Global vars //////////////
var gProvider;
var gSigner;
var gAddress;

// Unpkg imports
const Web3Modal = window.Web3Modal.default;
const WalletConnectProvider = window.WalletConnectProvider.default;
const evmChains = window.evmChains;

// Web3modal instance
let web3Modal;

/**
 * Kick in the UI action after Web3modal dialog has chosen a provider
 */
async function updateAccountModal() {
    // get connected address
    const addresses = await gProvider.listAccounts();
    const selectedAccount = addresses[0];
    let shortAddress =
        selectedAccount.slice(0, 6) + "..." + selectedAccount.slice(-4);
    document.querySelector("#selected-account").textContent = shortAddress;

    // get chain
    let chainId = await gProvider.send("eth_chainId");
    // turn to decimal
    chainId = parseInt(chainId, 16);
    const chainData = evmChains.getChain(chainId);
    document.querySelector("#selected-network").textContent = chainData.name;

    // get balance & format to 4 decimals
    let balance = await gProvider.getBalance(selectedAccount);
    balance = ethers.utils.formatEther(balance);
    balance = balance.slice(0, 8);
    document.querySelector("#selected-account-balance").textContent = balance;
}

/**
 * Fetch account data for UI when
 * - User switches accounts in wallet
 * - User switches networks in wallet
 * - User connects wallet initially
 */
async function refreshAccountData() {
    console.log("Refreshing account data");
    gAddress = await gSigner.getAddress();
    Alpine.store("gAddress", gAddress);

    // update connectButtonContent
    let shortAddress = gAddress.slice(0, 6) + "..." + gAddress.slice(-4);
    Alpine.store("connectButtonContent", shortAddress);

    Alpine.store("connected", true);

    // replace x-on:click of #connectButton with toggling showAccountModal
    document
        .querySelector("#connectButton")
        .setAttribute("x-on:click", "showAccountModal = !showAccountModal");
    updateAccountModal();

    // Disable button while UI is loading.
    // updateAccountModal() will take a while as it communicates
    // with Ethereum node via JSON-RPC and loads chain data
    // over an API call.
    // document.querySelector("#connectButton").setAttribute("disabled", "disabled");
    // await updateAccountModal(gProvider);
    // document.querySelector("#connectButton").removeAttribute("disabled");

    // if we are currently in /send
    if (window.location.pathname == "/send") {
        Alpine.store("sendButtonContent", "Send Crypto");
    }
}

/**
 * Adds listeners to provider
 * @param {Object} provider (ethers.js provider)
 **/
async function addListenersToProvider(provider) {
    // Subscribe to accounts, chainId and network changes
    provider.provider.on("accountsChanged", (accounts) => {
        // updateAccountModal();
        refreshAccountData();
    });
    provider.provider.on("chainChanged", (chainId) => {
        // updateAccountModal();
        refreshAccountData();
    });
    provider.provider.on("networkChanged", (networkId) => {
        // updateAccountModal();
        refreshAccountData();
    });
}

/**
 * Connect wallet button pressed.
 */
async function onConnect() {
    console.log("Opening a dialog", web3Modal);
    try {
        const connection = await web3Modal.connect();
        gProvider = new ethers.providers.Web3Provider(connection, "any");
        gSigner = gProvider.getSigner();

        await refreshAccountData();
        await addListenersToProvider(gProvider);
    } catch (e) {
        console.log("Could not get a wallet connection", e);
        return;
    }
}

/**
 * Setup the orchestra
 */
async function connectInit() {
    console.log("WalletConnectProvider is", WalletConnectProvider);
    console.log("window.ethereum is", window.ethereum);

    // Check that the web page is run in a http/https context,
    // as otherwise MetaMask won't be available
    if (location.protocol !== "http:" && location.protocol !== "https:") {
        // https://ethereum.stackexchange.com/a/62217/620
        const alert = document.querySelector("#alert-error-https");
        alert.style.display = "block";
        document
            .querySelector("#connectButton")
            .setAttribute("disabled", "disabled");
        return;
    }

    // Tell Web3modal what providers we have available.
    // Built-in web browser provider (only one can exist as a time)
    // like MetaMask, Brave or Opera is added automatically by Web3modal
    const providerOptions = {
        walletconnect: {
            package: WalletConnectProvider,
            options: {
                // test key
                infuraId: "c710a08b1dd6455b9090ec10aed18a96",
            },
        },

        // TODO: add more providers here (Argent, Authereum, Rainbow, etc.)
    };

    // should cache provider
    web3Modal = new Web3Modal({
        cacheProvider: true, // optional
        providerOptions, // required
        disableInjectedProvider: false, // optional. For MetaMask / Brave / Opera.
    });

    console.log("Web3Modal instance is", web3Modal);

    const cachedProvider = web3Modal.cachedProvider;
    if (cachedProvider) {
        console.log(
            "Found cached provider, trying to automatically reconnect (" +
            cachedProvider +
            ")",
        );
        try {
            // If users wallet is locked, this should not request a connection...
            if (cachedProvider === "injected") {
                // check if wallet is locked
                const provider = new ethers.providers.Web3Provider(
                    window.ethereum,
                    "any",
                );
                const addresses = await provider.listAccounts();
                if (!addresses.length) {
                    throw new Error("Wallet is locked");
                }
            }

            const connection = await web3Modal.connect();
            gProvider = new ethers.providers.Web3Provider(connection, "any");
            gSigner = gProvider.getSigner();

            await addListenersToProvider(gProvider);
            await refreshAccountData();
        } catch (e) {
            console.log("Could not get a wallet connection", e);
            return;
        }
    } else {
        console.log("No cached provider found");
    }
}

async function isConnected() {
    // returns true if connected to wallet
    if (gProvider) {
        const addresses = await gProvider.listAccounts();
        if (addresses.length) {
            return true;
        }
    }
    return false;
}

/**
 * Disconnect wallet button pressed.
 */
async function onDisconnect() {
    console.log("Killing the wallet connection");

    // TODO: Which providers have close method?
    if (gProvider.provider.close) {
        await gProvider.provider.close();

        // If the cached provider is not cleared,
        // WalletConnect will default to the existing session
        // and does not allow to re-scan the QR code with a new wallet.
        // Depending on your use case you may want or want not his behavir.
        await web3Modal.clearCachedProvider();
        gProvider.provider = null;
    }
}

/**
 * Main entry point.
 */
window.addEventListener("load", async () => {
    connectInit();
});
