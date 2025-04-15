const fs = require("fs");
const path = require("path");

// 👇 Replace this with your actual deployed contract address from Ganache
const deployedAddress = "0xae8EBB932ABaf93b9d54e60c445DCA3e354357fa";

function saveABI() {
  const artifactPath = path.join(__dirname, "../artifacts/contracts/TrafficEventLogger.sol/TrafficEventLogger.json");

  // Read the ABI from the compiled artifact
  const abi = JSON.parse(fs.readFileSync(artifactPath, "utf8")).abi;

  // Write ABI and address to frontend/src folder
  const outputPath = path.join(__dirname, "../../rsu/contract_details/TrafficEventLogger.json");
  fs.writeFileSync(
    outputPath,
    JSON.stringify({ address: deployedAddress, abi }, null, 2)
  );

  console.log("✅ ABI and address saved to rsu/contract_details/TrafficEventLogger.json");
}

saveABI();
