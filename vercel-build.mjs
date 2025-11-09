import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('Starting memory-optimized build process...');

// Function to run a command with memory limits
function runCommand(cmd, cwd = process.cwd(), env = {}) {
  console.log(`Running: ${cmd}`);
  try {
    execSync(cmd, { 
      stdio: 'inherit', 
      cwd, 
      env: { 
        ...process.env,
        NODE_OPTIONS: '--max_old_space_size=768',
        ...env
      } 
    });
    return true;
  } catch (error) {
    console.error(`Command failed: ${cmd}`, error);
    return false;
  }
}

// Main build process
async function main() {
  const frontendDir = 'front-end';
  
  console.log('Installing production dependencies only...');
  if (!runCommand('npm ci --prefer-offline --no-audit --no-optional --production', frontendDir)) {
    console.log('Falling back to npm install...');
    if (!runCommand('npm install --prefer-offline --no-audit --no-optional --production', frontendDir)) {
      process.exit(1);
    }
  }

  console.log('Installing dev dependencies...');
  if (!runCommand('npm install --prefer-offline --no-audit --no-optional --only=dev', frontendDir)) {
    process.exit(1);
  }

  console.log('Running build with memory optimization...');
  if (!runCommand('NODE_OPTIONS=--max_old_space_size=768 npx vite build --mode production', frontendDir, {
    NODE_OPTIONS: '--max_old_space_size=768',
    NODE_ENV: 'production',
    GENERATE_SOURCEMAP: 'false'
  })) {
    console.log('Build failed, trying with source maps disabled...');
    if (!runCommand('NODE_OPTIONS=--max_old_space_size=768 GENERATE_SOURCEMAP=false npx vite build --mode production', frontendDir)) {
      process.exit(1);
    }
  }

  console.log('Build completed successfully!');
}

main().catch(console.error);
