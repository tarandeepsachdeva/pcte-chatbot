const { execSync } = require('child_process');
const fs = require('fs');

console.log('Starting optimized build process...');

// Function to run a command with memory limits
function runCommand(cmd, cwd = process.cwd()) {
  console.log(`Running: ${cmd}`);
  try {
    execSync(cmd, { stdio: 'inherit', cwd, env: { ...process.env, NODE_OPTIONS: '--max_old_space_size=1024' } });
    return true;
  } catch (error) {
    console.error(`Command failed: ${cmd}`, error);
    return false;
  }
}

// Main build process
function main() {
  const frontendDir = 'front-end';
  
  console.log('Installing dependencies...');
  if (!runCommand('npm install --no-audit --prefer-offline', frontendDir)) {
    process.exit(1);
  }

  console.log('Running build...');
  if (!runCommand('npm run build', frontendDir)) {
    process.exit(1);
  }

  console.log('Build completed successfully!');
}

main();
