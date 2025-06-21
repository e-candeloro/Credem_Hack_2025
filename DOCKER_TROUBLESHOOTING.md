# Docker Troubleshooting Guide

## Issue: "No files found in tmp/" when running in Docker

### Problem Description
When running the application locally, it works fine, but when running in Docker, you get the error "No files found in tmp/".

### Root Causes
1. **Missing `tmp/` directory**: The Docker container doesn't have the `tmp/` directory created
2. **GCS authentication issues**: The container can't authenticate with Google Cloud Storage
3. **Environment variables not set**: Required environment variables are missing
4. **File download failures**: Files are not being downloaded from GCS bucket

### Solutions

#### 1. Setup GCP Authentication (Required First Step)
Before running the Docker container, you need to authenticate with Google Cloud:

```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate with your Google Cloud account
gcloud auth login

# Set up Application Default Credentials (ADC)
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Check Docker Environment
Run the debug script to check the Docker environment:

```bash
# On Linux/Mac
./run_docker_debug.sh

# On Windows
run_docker_debug.bat
```

Or manually:
```bash
docker build -t credem-hack-app .
docker run --rm -v ~/.config/gcloud:/root/.config/gcloud credem-hack-app python -c "
import os
print('Current working directory:', os.getcwd())
print('tmp/ exists:', os.path.exists('tmp'))
print('GCP config exists:', os.path.exists('/root/.config/gcloud'))
"
```

#### 3. Set Environment Variables
Make sure all required environment variables are set when running Docker:

```bash
docker run --rm \
  -v ~/.config/gcloud:/root/.config/gcloud \
  -e DEBUG=True \
  -e PROJECT_ID=your_project_id \
  -e INPUT_BUCKET=your_input_bucket \
  -e OUTPUT_BUCKET=your_output_bucket \
  -e LOCATION=us \
  -e PROCESSOR_ID=your_processor_id \
  -e GOOGLE_API_KEY=your_api_key \
  credem-hack-app
```

#### 4. GCS Authentication
The application uses Application Default Credentials (ADC) which are automatically configured by gcloud CLI:

**Standard Approach (Recommended)**:
```bash
# 1. Set up ADC locally
gcloud auth application-default login

# 2. Run Docker with volume mount
docker run --rm \
  -v ~/.config/gcloud:/root/.config/gcloud \
  -e PROJECT_ID=your_project_id \
  -e INPUT_BUCKET=your_input_bucket \
  -e OUTPUT_BUCKET=your_output_bucket \
  credem-hack-app
```

**Alternative: Service Account Key** (if ADC doesn't work):
```bash
docker run --rm \
  -v /path/to/service-account-key.json:/app/service-account-key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
  -e PROJECT_ID=your_project_id \
  -e INPUT_BUCKET=your_input_bucket \
  -e OUTPUT_BUCKET=your_output_bucket \
  credem-hack-app
```

#### 5. Check GCS Bucket Contents
Verify that your GCS bucket contains files in the `input/` prefix:

```bash
gsutil ls gs://your_input_bucket/input/
```

#### 6. Manual Testing Steps

1. **Test GCS connection**:
   ```bash
   docker run --rm \
     -v ~/.config/gcloud:/root/.config/gcloud \
     -e PROJECT_ID=your_project_id \
     -e INPUT_BUCKET=your_input_bucket \
     credem-hack-app python -c "
   from gcs_utils import download_from_bucket
   from config import load_config
   config = load_config()
   files = download_from_bucket(config)
   print(f'Downloaded {len(files)} files')
   "
   ```

2. **Test tmp directory creation**:
   ```bash
   docker run --rm credem-hack-app python -c "
   import os
   os.makedirs('tmp', exist_ok=True)
   print(f'tmp exists: {os.path.exists(\"tmp\")}')
   print(f'tmp contents: {os.listdir(\"tmp\")}')
   "
   ```

### Debugging Information Added

The following improvements have been made to help with debugging:

1. **Enhanced logging** in `gcs_utils.py`:
   - Shows current working directory
   - Shows absolute path to tmp directory
   - Shows number of files found in bucket
   - Shows number of files successfully downloaded

2. **Enhanced logging** in `document_ai.py`:
   - Shows current working directory when tmp folder doesn't exist
   - Shows absolute path to tmp folder
   - Shows contents of tmp folder when empty
   - Lists all files found for processing

3. **Enhanced logging** in `main.py`:
   - Shows configuration loaded
   - Shows number of files downloaded
   - Shows progress through each pipeline stage

4. **Dockerfile improvements**:
   - Creates `tmp/` directory with proper permissions
   - Simplified to use standard GCP credentials path

5. **Simplified run scripts**:
   - Use default GCP credentials from gcloud CLI
   - Automatically mount `~/.config/gcloud` to container
   - Check for gcloud configuration before running

### Common Issues and Solutions

#### Issue: "Permission denied accessing tmp/"
**Solution**: The Dockerfile now creates the tmp directory with proper permissions.

#### Issue: "No such file or directory: tmp/"
**Solution**: The Dockerfile now explicitly creates the tmp directory.

#### Issue: "Authentication failed for GCS"
**Solution**:
1. Run `gcloud auth application-default login` locally
2. Make sure the `~/.config/gcloud` directory is mounted to the container
3. Verify your project has the necessary GCS permissions

#### Issue: "Environment variables not found"
**Solution**: Set all required environment variables when running Docker (see section 3 above).

#### Issue: "gcloud configuration not found"
**Solution**: Run `gcloud auth application-default login` to set up Application Default Credentials.

### Testing the Fix

After applying the fixes:

1. **Set up GCP authentication**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t credem-hack-app .
   ```

3. **Run with proper environment variables**:
   ```bash
   docker run --rm \
     -v ~/.config/gcloud:/root/.config/gcloud \
     -e DEBUG=True \
     -e PROJECT_ID=your_project_id \
     -e INPUT_BUCKET=your_input_bucket \
     -e OUTPUT_BUCKET=your_output_bucket \
     -e LOCATION=us \
     -e PROCESSOR_ID=your_processor_id \
     -e GOOGLE_API_KEY=your_api_key \
     credem-hack-app
   ```

4. **Check the logs for detailed debugging information**.

### Additional Notes

- The `tmp/` directory is now created in the Dockerfile with proper permissions
- Enhanced logging will help identify exactly where the issue occurs
- The application now uses Application Default Credentials (ADC) from gcloud CLI
- The `~/.config/gcloud` directory is automatically mounted to provide GCP authentication
- Environment variables must be properly set for GCS authentication and bucket access
- The run scripts automatically check for gcloud configuration before running
