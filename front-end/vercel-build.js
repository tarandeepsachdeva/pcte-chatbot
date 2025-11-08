const { execSync } = require('child_process');
const fs = require('fs');

console.log('Running vercel-build.js...');

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
  
  // Build the frontend
  console.log('Building frontend...');
  execSync('npm run build', { stdio: 'inherit' });
  console.log('Frontend built successfully');
} catch (error) {
  console.error('Error during build:', error);
  process.exit(1);
}
