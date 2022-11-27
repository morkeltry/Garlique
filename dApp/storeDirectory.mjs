//////////////////////////////////////////
// storeDirectory.mjs
// Stores a directory of files in IPFS using nft.storage API
// usage: $ node storeDirectory.mjs <directory-path>


import { NFTStorage } from 'nft.storage'
import { filesFromPath } from 'files-from-path'
import path from 'path'
import dotenv from 'dotenv'

// load ../.env file
dotenv.config()

const token = process.env.NFT_STORAGE_API_KEY

async function main(ignoreDirs=true) {
  // you'll probably want more sophisticated argument parsing in a real app
  if (process.argv.length !== 3) {
    console.error(`usage: ${process.argv[0]} ${process.argv[1]} <directory-path>`)
  }
  const directoryPath = process.argv[2]
  const files = filesFromPath(directoryPath, {
    pathPrefix: path.resolve(directoryPath),
    hidden: false, // IMPORTANT to ignore hidden files
  })

  if (ignoreDirs) {
    var filesToStore = []
    for await (const file of files) {
      let name = file.name
      // if more than one / in name, it's a subdirectory
      if (name.split('/').length > 2) {
        continue
      }
      filesToStore.push(file)
    }
  } else {
    filesToStore = files
  }

  const storage = new NFTStorage({ token })

  console.log(`storing file(s) from ${path}`)
  const cid = await storage.storeDirectory(filesToStore)
  console.log({ cid })

  const status = await storage.status(cid)
  console.log(status)
}
main()