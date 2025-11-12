# Video Stream Demo

A FastAPI-based video streaming application that uploads videos to AWS S3 and stores metadata in PostgreSQL. It provides endpoints for uploading videos, retrieving metadata, generating presigned S3 URLs, and streaming videos directly through the application.

## Features

- **Video Upload**: Upload video files to AWS S3 with automatic metadata storage
- **Metadata Storage**: PostgreSQL database for video information (filename, MIME type, S3 key, timestamps)
- **Presigned URLs**: Generate temporary S3 URLs for direct client-to-S3 downloads
- **Proxy Streaming**: Stream videos through the application server
- **FastAPI**: Modern, fast web framework with automatic API documentation

## Prerequisites

- Python 3.8+
- PostgreSQL 16+ (local or remote)
- AWS S3 bucket and credentials
- AWS CLI (optional, for testing S3 connectivity)

## Installation

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git postgresql-client
```

### 2. Clone and Set Up the Project

```bash
# Clone the repository
git clone https://github.com/mateofloreza/video-stream-demo.git
cd video-stream-demo

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn boto3 sqlalchemy psycopg2-binary python-multipart pydantic
```

### 3. Configure Environment Variables

Create a `.env` file in your home directory or project root:

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="eu-central-1"
export S3_BUCKET="your-bucket-name"
export DATABASE_URL="postgresql+psycopg2://user:password@host:5432/database"
```

Load the environment variables:

```bash
source ~/.env
```

### 4. Verify AWS S3 Connectivity (Optional)

```bash
# Install AWS CLI if not already installed
sudo apt install -y awscli
# or
sudo snap install aws-cli --classic

# Test S3 access
aws s3 ls s3://$S3_BUCKET
aws s3api get-bucket-location --bucket $S3_BUCKET
```

### 5. Verify PostgreSQL Setup

Connect to your PostgreSQL database:

```bash
psql $DATABASE_URL
```

Once connected, verify the tables:

```sql
-- List tables
\dt

-- Check videos table structure
\d videos

-- View existing videos (if any)
SELECT * FROM videos;
```

Expected table structure:

```
 Schema |  Name  | Type  |     Owner      
--------+--------+-------+----------------
 public | videos | table | database_owner
```

## Running the Application

### Start the Development Server

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Load environment variables
source ~/.env

# Start the server
uvicorn main:app --reload --port 8000
```

To make the server accessible from other machines:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### 1. Upload a Video

```bash
POST /upload
```

Upload a video file to S3 and store metadata in the database.

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Accept: application/json" \
  -F "file=@sample.mp4;type=video/mp4"
```

**Response:**

```json
{
  "id": 1,
  "filename": "sample.mp4",
  "mime_type": "video/mp4",
  "s3_key": "uploads/687f1191ba654c60a85efdc24dc0f01c_sample.mp4",
  "created_at": "2025-11-12T10:33:17.631751+00:00"
}
```

### 2. Get Video Metadata

```bash
GET /videos/{video_id}
```

Retrieve metadata for a specific video.

**Example:**

```bash
curl http://127.0.0.1:8000/videos/1
```

**Response:**

```json
{
  "id": 1,
  "filename": "sample.mp4",
  "mime_type": "video/mp4",
  "s3_key": "uploads/687f1191ba654c60a85efdc24dc0f01c_sample.mp4",
  "created_at": "2025-11-12T10:33:17.631751+00:00"
}
```

### 3. Get Presigned Stream URL

```bash
GET /videos/{video_id}/stream-url
```

Generate a temporary presigned URL for direct S3 access (expires in 1 hour).

**Example:**

```bash
curl http://127.0.0.1:8000/videos/1/stream-url
```

**Response:**

```json
{
  "url": "https://s3.eu-central-1.amazonaws.com/your-bucket/uploads/...",
  "expires_in": 3600
}
```

### 4. Stream Video (Proxy)

```bash
GET /videos/{video_id}/stream
```

Stream video through the application server (hides S3 keys from clients).

**Example:**

```bash
# Stream in browser
http://127.0.0.1:8000/videos/1/stream

# Or download with curl
curl http://127.0.0.1:8000/videos/1/stream -o downloaded_video.mp4
```

## Testing

### Download a Sample Video

```bash
wget https://videos.pexels.com/video-files/5752729/5752729-uhd_3840_2160_30fps.mp4 -O sample.mp4
```

### Complete Test Flow

```bash
# 1. Upload a video
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Accept: application/json" \
  -F "file=@sample.mp4;type=video/mp4"

# 2. Get video metadata (replace {id} with returned ID)
curl http://127.0.0.1:8000/videos/1

# 3. Get presigned URL
curl http://127.0.0.1:8000/videos/1/stream-url

# 4. Stream video
curl http://127.0.0.1:8000/videos/1/stream -o test_stream.mp4
```

### Verify Database Records

```bash
psql $DATABASE_URL -c "SELECT * FROM videos;"
```

## Advanced Setup (Optional)

### Setting Up with Juju (for Production Deployment)

If you want to deploy using Juju with LXD:

```bash
# Install LXD and Juju
sudo snap install lxd --channel 5.21/stable
lxd init --auto
lxc network set lxdbr0 ipv6.address none
sudo snap install juju --channel 3/stable

# Bootstrap Juju
juju bootstrap localhost

# Deploy PostgreSQL
juju deploy postgresql --channel=16/stable
juju deploy data-integrator data-integrator-postgresql --config database-name=field-video
juju integrate postgresql data-integrator-postgresql

# Get database credentials
juju run data-integrator-postgresql/0 get-credentials
```

### Remote Access via VPN

To access a remote deployment from your local machine:

```bash
sshuttle -r ubuntu@<remote-ip> 10.0.0.0/8
```

## Project Structure

```
.
├── main.py          # FastAPI application and routes
├── database.py      # SQLAlchemy database configuration
├── models.py        # Database models (Video table)
├── schemas.py       # Pydantic schemas for request/response
├── s3client.py      # AWS S3 client and helper functions
├── README.md        # This file
└── LICENSE          # License file
```

## License

See the [LICENSE](LICENSE) file for details.

