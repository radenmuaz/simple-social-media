# simple-social-media

Instagram-like social media app.

## dev

`main.py` is FastAPI code, run with `uvicorn main:app` command.
`models.py` is `sqlalchemy` database models.
`pydantic_models.py` is `pydantic` models.
`test.py` is simple test code to dry run all the available api endpoints.
`frontend` contains js frontend written in Solid.js .

Database is created as sqlite `app.db` in first run.
To reset, simply delete `app.db`.

```
python3 -m venv ~/server_venv
. ~/server_venv/bin/activate
python3 -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# in another terminal
cd frontend
npm install
npm dev run
# open http://localhost:5173/

# to build to frontend/dist/{index.html, assets, etc.}
npm dev build

# to reset
rm app.db
```

## deploy

Deployment here is extremely simple and unsafe. No https, public IP without domain, uvicorn run inside tmux.
This is what I can do in ~10 hours work spread over ~3 days.
In real deployment, something like https cert, domain name, docker and auto-restart services wiht workers are more practical.

Here, assume there is web server `web` with admin username `raden_m_muaz` and with firewall tcp port 8000 allowed.

0. Edit `frontend/src/config.js`, key in the IP address of machine, then rebuild with `cd frontend && npm install && npm build`
```
const config = {
    API_URL: process.env.NODE_ENV === 'production'
        ? "http://YOUR_MACHINE_IP:8000"
        : "http://localhost:8000",
    
    IMAGE_URL: process.env.NODE_ENV === 'production'
        ? "http://YOUR_MACHINE_IP:80"
        : "http://localhost:8000",
};

export default config;

```

1. Upload to machine

```
pwd # make sure you are in this repo
cd ..
scp -r simple-social-media raden_m_muaz@web:/home/raden_m_muaz
# gcloud compute scp --recurse simple-social-media raden_m_muaz@web:/home/raden_m_muaz
```

then ssh to the machine

```
ssh raden_m_muaz@web
# gcloud compute ssh raden_m_muaz@web
```

2. Install Apache and prepare js frontend to Apache hosting folder.

```
sudo apt-get install apache2 php7.0 zip python3-pip python3.11-venv tmux
export UPLOAD_DIR_ROOT=/var/www/html/
sudo mkdir -p $UPLOAD_DIR_ROOT/static/uploads
sudo chmod 755 $UPLOAD_DIR_ROOT/static/uploads
sudo chown raden_m_muaz:raden_m_muaz $UPLOAD_DIR_ROOT/static/uploads
sudo cp -r ~/simple-social-media/frontend/dist/* /var/www/html
```

3. Run FastAPI server
```
tmux
export PUBLIC_IP=http://<IP>
python3 -m venv ~/server_venv
. ~/server_venv/bin/activate
cd ~/simple-social-media
python3 -m pip install -r requirements.txt
export UPLOAD_DIR_ROOT=/var/www/html/
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
## alternative:
# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80

## Ctrl-B, D to detach
## to attach:
tmux attach
```

4. Open your browser IP
Note: use http://ip without https
