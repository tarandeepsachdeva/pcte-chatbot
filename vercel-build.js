const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Starting Vercel build process...');

// Install frontend dependencies
console.log('Installing frontend dependencies...');
try {
  execSync('cd front-end && npm install', { stdio: 'inherit' });
  console.log('Frontend dependencies installed successfully');
  
  // Build the frontend
  console.log('Building frontend...');
  execSync('cd front-end && npm run build', { stdio: 'inherit' });
  console.log('Frontend built successfully');
} catch (error) {
  console.error('Error during frontend build:', error);
  process.exit(1);
}

// Install Python dependencies if requirements.txt exists
if (fs.existsSync('front-end/requirements.txt')) {
  console.log('Installing Python dependencies...');
  try {
    execSync('pip3 install -r front-end/requirements.txt --target .python_packages', { stdio: 'inherit' });
    console.log('Python dependencies installed successfully');
  } catch (error) {
    console.error('Error installing Python dependencies:', error);
    process.exit(1);
  }
}
