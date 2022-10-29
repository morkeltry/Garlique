import { ClientCtrl, ConfigCtrl } from '@web3modal/core'
// import { ClientCtrl, ConfigCtrl } from '../node_modules/@web3modal/core'
import { chains, providers } from '@web3modal/ethereum'
// import { chains, providers } from '../node_modules/@web3modal/ethereum'
import '@web3modal/ui'
// import '../node_modules/@web3modal/ui'
import './actions.js'
import './events.js'

// Define constants
const PROJECT_ID = 'f4de2e260c40f83bdf011443ab71c33b'  // walletconnect project id

const clientConfig = {
  projectId: PROJECT_ID,
  theme: 'dark',
  accentColor: 'default'
}

const ethereumConfig = {
  appName: 'web3Modal',
  autoConnect: true,
  chains: [chains.mainnet],
  providers: [providers.walletConnectProvider({ projectId: PROJECT_ID })]
}

// Set up core and ethereum clients
ConfigCtrl.setConfig(clientConfig)
ClientCtrl.setEthereumClient(ethereumConfig)
