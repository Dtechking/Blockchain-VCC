const { ethers } = require("hardhat");

async function main() {
  const TrafficEventLogger = await ethers.getContractFactory("TrafficEventLogger");

  console.log("⏳ Deploying contract...");
  const trafficEventLogger = await TrafficEventLogger.deploy();

  console.log("⛏ Waiting for deployment...");
  await trafficEventLogger.waitForDeployment(); // For Hardhat Ethers v6+

  console.log("✅ Contract deployed at:", await trafficEventLogger.getAddress());
}

main().catch((error) => {
  console.error("❌ Error deploying contract:", error);
  process.exitCode = 1;
});
