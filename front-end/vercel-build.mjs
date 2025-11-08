import { execSync } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('Running vercel-build.mjs...');

// Install Python dependencies
if (fs.existsSync('requirements.txt')) {
  console.log('Installing Python dependencies...');
  try {
    execSync('pip3 install -r requirements.txt --target .python_packages', { stdio: 'inherit' });
    console.log('Python dependencies installed successfully');
  } catch (error) {
    console.error('Error installing Python dependencies:', error);
    process.exit(1);
  }
}

// Install Node.js dependencies
console.log('Installing Node.js dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('Node.js dependencies installed successfully');
} catch (error) {
  console.error('Error installing Node.js dependencies:', error);
  process.exit(1);
}

// Run the build
console.log('Running build...');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('Build completed successfully');
} catch (error) {
  console.error('Error during build:', error);
  process.exit(1);
}
