// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
//
// You can also run a script with `npx hardhat run <script>`. If you do that, Hardhat
// will compile your contracts, add the Hardhat Runtime Environment's members to the
// global scope, and execute the script.
const hre = require("hardhat");


async function main(garlicPatch) {

  const Garlique = await hre.ethers.getContractFactory("Garlique");
  const garlique = await Garlique.deploy(garlicPatch);

  await garlique.deployed();

  console.log(
    `Deployed to ${garlique.address}`
  );
}

import("../constants/garlic_patch.mjs")
  .then (({garlicPatch}) => {    
    console.log (`Deploying with server addy: ${garlicPatch}`);
    // We recommend this pattern to be able to use async/await everywhere
    // and properly handle errors.
    main(garlicPatch).catch((error) => {
      console.error(error);
      process.exitCode = 1;
    });
})
