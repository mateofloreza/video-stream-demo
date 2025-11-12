# video-stream-demo

install app:

sudo apt update
sudo apt install -y postgresql-client
psql postgresql://relation-34:UbskJ62yhxTlz6BI@10.60.222.43:5432/field-video
mkdir ~/video_demo && cd ~/video_demo
python3 -m venv venv
sudo apt install -y python3 python3-venv python3-pip git
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn boto3 sqlalchemy psycopg2-binary python-multipart pydantic
vim database.py
vim models.py
vim schemas.py
vim s3client.py
vim main.py
unicorn main:app --reload --port 8000
uvicorn main:app --reload --port 8000
cd ..
vim .env
source .env 
env
env |grep DA
sudo apt install -y awscli
sudo snap install aws-cli --classic
aws s3 ls s3://$S3_BUCKET
uvicorn main:app --reload --port 8000
cd video_demo/
uvicorn main:app --reload --port 8000
aws s3api get-bucket-location --bucket field-video
uvicorn main:app --reload --port 8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000

(venv) ubuntu@juju-ed8fe0-19:~/video_demo$ cat ~/.env 
export AWS_ACCESS_KEY_ID="XXXXXXX"
export AWS_SECRET_ACCESS_KEY="XXXXXXX"
export AWS_REGION="eu-central-1"
export S3_BUCKET="field-video"
export DATABASE_URL="postgresql+psycopg2://relation-34:UbskJ62yhxTlz6BI@10.60.222.43:5432/field-video"


verify postgresql metadata:

psql postgresql://relation-34:UbskJ62yhxTlz6BI@10.60.222.43:5432/field-video
psql (16.10 (Ubuntu 16.10-0ubuntu0.24.04.1))
Type "help" for help.

field-video=> \dt
Did not find any relations.
field-video=> \dt
                  List of relations
 Schema |  Name  | Type  |           Owner           
--------+--------+-------+---------------------------
 public | videos | table | charmed_field-video_owner
(1 row)

field-video=> SELECT * FROM videos;
 id |  filename  | mime_type |                       s3_key                        |          created_at           
----+------------+-----------+-----------------------------------------------------+-------------------------------
  1 | sample.mp4 | video/mp4 | uploads/687f1191ba654c60a85efdc24dc0f01c_sample.mp4 | 2025-11-12 10:33:17.631751+00
(1 row)

field-video=> SELECT * FROM videos;
 id |  filename  | mime_type |                       s3_key                        |          created_at           
----+------------+-----------+-----------------------------------------------------+-------------------------------
  1 | sample.mp4 | video/mp4 | uploads/687f1191ba654c60a85efdc24dc0f01c_sample.mp4 | 2025-11-12 10:33:17.631751+00
(1 row)


test apis:

wget https://videos.pexels.com/video-files/5752729/5752729-uhd_3840_2160_30fps.mp4 -O sample.mp4
curl -X POST "http://127.0.0.1:8000/upload"   -H "Accept: application/json"   -F "file=@sample.mp4;type=video/mp4"
curl http://127.0.0.1:8000/videos/1
curl http://127.0.0.1:8000/videos/1/stream-url
stream: http://10.60.222.172:8000/videos/1/stream

local machine vpn:
sshuttle -r ubuntu@52.58.107.84 10.0.0.0/8

Install: 
sudo snap install lxd --channel 5.21/stable
lxd init --auto                                                                                                                                                       
lxc network set lxdbr0 ipv6.address none                                                                                                                              
sudo snap install juju --channel 3/stable                                                                                                                             
juju bootstrap localhost                                                                                                                                              
juju add-model field-siem

cat <<EOF > cloudinit-userdata.yaml
cloudinit-userdata: |
  postruncmd:
    - [ 'echo', 'vm.max_map_count=262144', '>>', '/etc/sysctl.conf' ]
    - [ 'echo', 'vm.swappiness=0', '>>', '/etc/sysctl.conf' ]
    - [ 'echo', 'net.ipv4.tcp_retries2=5', '>>', '/etc/sysctl.conf' ]
    - [ 'echo', 'fs.file-max=1048576', '>>', '/etc/sysctl.conf' ]
    - [ 'sysctl', '-p' ]
EOF
juju model-config --file=./cloudinit-userdata.yaml

juju deploy postgresql --channel=16/stable
juju add-secret field-video operator=ubuntu
juju grant-secret field-video postgresql
juju config postgresql system-users=secret:d4a5hi9uib2cg7atelq0
juju ssh --container postgresql postgresql/leader bash

juju deploy data-integrator data-integrator-postgresql --config database-name=field-video
juju deploy ubuntu video-field
juju integrate postgresql data-integrator-postgresql

juju run data-integrator-postgresql/0 get-credentials


