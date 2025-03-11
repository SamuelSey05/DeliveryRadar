# DeliveryRadar

## Project Summary

## Running the Application

### Basics

First clone the repository to your device/server.

```Bash
mkdir -p $HOME/app
cd $HOME/app

# Clone all branches, recommended for development
git clone https://github.com/SamuelSey05/DeliveryRadar.git

# Or clone only the main branch, recommended for deployment
git clone -b main --single-branch https://github.com/SamuelSey05/DeliveryRadar.git
```

Open the repository, and run the build script - this installs dependencies and builds the frontend modules.

```Bash
cd $HOME/app/DeliveryRadar
./build.sh
```

To run the application for testing, setup secrets (see [#Secrets](#secrets) below), then run the command `flask run` from the project root. This will open up a server listening on [localhost:5000](https://localhost:5000).

### Deployment

The below documents the deployment used on [our prototype site](cstdeliveryradar.soc.srcf.net), for future reference and also as advice for other deployments.

> Note: The below assumes the use of *Bash* as your preferred `$SHELL`, if you use a different `$SHELL` (zsh, ...), you may need to adapt these instructions. Refer to documentation for individual projects if needed.

#### Pyenv

The version of Python used on a webserver may vary, as the application is written for Python 3.11, it is best to guarantee that this is the version running. On most linux distributions, the best way of doing this, is with [Pyenv](https://github.com/pyenv/pyenv). Perform the following as your deployment user:

```Bash
# Change to $HOME directory
cd $HOME

# Install pyenv in $HOME/.pyenv
curl -fsSL https://pyenv.run | bash

# Add pyenv installation to $PATH
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

# Reload shell to enable pyenv
. .bashrc

# Install Python 3.11
pyenv install 3.11

# Set python version as active globally within the userspace
pyenv global 3.11
# Or set for only the deployment
cd app/DeliveryRadar # Replace with path to your cloned repo
pyenv local 3.11
```

#### NVM

Similarly to Python, the application requires a specific version of node.js (v18). [NVM](https://github.com/nvm-sh/nvm) is the equivalent of pyenv to specify the version in use.

```Bash
# Change to $HOME directory
cd $HOME

# Install NVM, this should automatically setup .bashrc to make use of it.
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Reload .bashrc to enable NVM
. .bashrc

# Install Node.js 18 and update NPM, this will be set as the default in new shells
nvm install 18
nvm install-latest-npm

# Reload .bashrc again to load Node.js 18
. .bashrc
```

#### Creating a Virtual Environment

The ideal when creating/running Python applications is to install dependencies in a project local directory, as a Virtual Environment (venv).

```Bash
# Change to cloned Repo directory, replace with your own path
cd $HOME/app/DeliveryRadar

# Create a venv, in the directory .venv
python -m venv .venv

# Load the venv
. .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Gunicorn

Using `flask run` is okay for development, but not deployment for production. On your deployed server, we recommend using gunicorn as the WGSI backend that then interfaces with Flask. To use gunicorn, perform the following:

```Bash
cd $HOME/app
touch run.sh
chmod +x run.sh
$EDITOR run.sh
```

This will create a new script file, `run.sh`, and open it in your chosen `$EDITOR`. In the file, place the following, replacing home with the location of your user's home directory, which can be found using the command `echo "$HOME"`, if you aren't sure.

```Bash
#!/usr/bin/env bash

app="app:app"
root="$HOME/app/DeliveryRadar"
socket="$HOME/app/DeliveryRadar.sock"

cat <<EOF
---
gunicorn: $(which gunicorn)
app: $app ($(realpath "$root"))
socket: $(realpath "$socket")
---
EOF

# Change directory to the project root, relative to this script.
# This means you don't need to be in the directory yourself to run it.

cd "$(dirname $(realpath "$0"))"
cd "$root"

# Options applied to gunicorn:
#
# - reload: Watch for code changes and restart the app as needed.
# - access-logfile: Log HTTP requests received by the app.
# - access-logformat: Use X-Forwarded-For for end-user access IPs.
# - error-logfile: Log error messages from gunicorn and its workers.
# - bind: Expose the app on a Unix socket.
#
# Other useful options if you have a newer version of gunicorn:
#
# - capture-output: Print app output and tracebacks.
#
# Documentation: https://docs.gunicorn.org/en/stable/settings.html

logfmt='%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

exec gunicorn \
  --reload \
  --access-logfile - \
  --access-logformat "$logfmt" \
  --error-logfile - \
  --bind "unix:$socket" \
  --capture-output \
  "$app"
```

This script, when run, will start the application listening on the UNIX socket `$HOME/app/DeliveryRadar.sock`. To then serve web requests to this, setup your web server to connect to that socket. The example shown below does this for an apache webserver in a `.htaccess` file, make sure you replace `$HOME` with it's path value:

```htaccess
# Force https
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301,NE]

# Set Header Forwarding
RequestHeader set Host expr=%{HTTP_HOST}
RequestHeader set X-Forwarded-For expr=%{REMOTE_ADDR}
RequestHeader set X-Real-IP expr=%{REMOTE_ADDR}
RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}

# Send requests for `/` to the Flask application socket.
RewriteRule "^(.*)$" unix:$HOME/app/DeliveryRadar.sock|http://%{HTTP_HOST}/$1 [P,QSA,NE,L]

# Prevents Default Apache file listing on root domain
DirectoryIndex disabled
```

#### SystemD

Starting gunicorn manually every time is less than ideal, so setup a systemd service to automatically start it upon restart:

```Bash
mkdir -p $HOME/.config/systemd/user
cd $HOME/.config/systemd/user
touch run.service
$EDITOR run.service
```

This will create a new service file `run.service`, and open it for editing. Add the following to the file:

```Systemd
[Unit]
Description="Flask Web Server"

[Install]
WantedBy=default.target

[Service]
WorkingDirectory=%h/app
ExecStart=/bin/bash %h/app/run.sh
Restart=always
ExecReload=/bin/kill -HUP $MAINPID
```

Similarly, a service can be created to update the application:

```Bash
cd $HOME/app
touch update.sh
chmod +x update.sh
$EDITOR update.sh

cd $HOME/.config/systemd/user
touch update.service
$EDITOR update.service

touch update.timer
$EDITOR update.timer
```

See below for the contents of these three files:

##### `update.sh`

```Bash
#!/usr/bin/env bash
systemctl --user stop run.service
. $HOME/.bashrc
. $HOME/app/DeliveryRaday/.venv/bin/activate
cd $HOME/app/DeliveryRadar
git fetch
git pull
$HOME/app/DeliveryRadar/build.sh
systemctl --user start run.service
```

##### `update.service`

```Systemd
[Unit]
Description=DeliveryRadar repository sync

[Install]
WantedBy=timers.target

[Service]
ExecStart=/bin/bash %h/app/update.sh
```

##### `update.timer`

```Systemd
[Timer]
# Currently set to update hourly, you may want to change frequency of updates for your deployment
OnCalendar=hourly
Unit=update.service
Persistent=true

[Install]
WantedBy=timers.target
```

Finally, reload systemd for your user and enable your new services:

```Bash
# Reload Systemd to pick up new services
systemctl --user daemon-reload

# Enable and Start run.service
systemctl --user enable run.service
systemctl --user start run.service

# Enable and start update timer
systemctl --user enable update.timer
systemctl --user start update.timer
```

### Options and Environment Variables

#### `config.py`

`config.py` is the file used to manage secrets for the application. To set these up, perform the following:

```Bash
cp config.py.template config.py
$EDITOR config.py
```

This will open up the file in your preferred `$EDITOR` application. You should see the following:

```Python
class DatabaseSecrets:
    host = ""
    user = ""
    database = ""
    password = ""

roboflow_key = ""
```

Fill in the details of your Database:

- hostname
- database name
- username
- password

Also fill in your [roboflow](https://roboflow.com/) API key. 

#### `DR_FLASK_LOCAL_TEST`

The database used by default can only be accessed on SRCF servers. To test the application without using the database, set the environment variable `DR_FLASK_LOCAL_TEST`. This will print the SQL statements that would be sent to the database to Stderr instead.

```Bash
export DR_FLASK_LOCAL_TEST=1
```

#### `DR_TEST_SCHED`

The video processing takes a long time. To test the rest of the application and skip the video processing stage, and instead return a random number from 0-15 for the speed, set the `DR_TEST_SCHED` environment variable.

```Bash
export DR_TEST_SCHED=1
```

#### `DR_DB_REMOTE_TEST`

The Database contains a flag to mark data submitted as test data. Set the `DR_DB_REMOTE_TEST` environment variable to mark data submitted by this instance of the application as test data.

```Bash
export DR_DB_REMOTE_TEST=1
```

## Dependencies

The application is written mostly in Python, aimed at version 3.11, and uses the following libraries:

- Serving the Website:
  - `gunicorn` (Used to serve the website)
  - `Flask`
- Database Connection:
  - `mysql-connector-python`
- Video Processing:
  - `deep-sort-realtime`
  - `inference-sdk`
  - `numpy`
  - `opencv-python`
  - `scipy`
  - `torchvision`
    - This depends on PyTorch, which can use various compute devices.
    - If using CPU Compute on x86_64, AVX2 ISA Extensions are required on a hardware level.
      - We ran afoul of this in our prototype deployment on a Xeon E5-2620 V2, but this shouldn't generally be a problem - 3rd Gen Intel and upwards should run without a problem.
    - If using GPU Compute, you may additionally need to install the CUDA packages for your system.
  
To install these packages, perform the following command from the root directory:

```bash
pip install -r requirements.txt
```
  
Additionally, the website frontend is written in React.js, using Node version 18. To install it's dependencies, perform the following commands from the root directory:

```Bash
cd videoUpload
npm install
```

The object recognition section of the video processing uses [roboflow](https://roboflow.com/). In particular, a pre-trained custom [Bikes-Peds-Scooters-v4 Model](https://universe.roboflow.com/engs-89/bikes-ped-scooters/model/4). You'll need to setup a free API key to access the model, and add this to `config.py`.

## Database

The database used has a single table: `Incidents`, which has six columns:

- `vehicle_id` - an auto incrementing integer used as a primary key - assume that all vehicles recorded are different
- `hash` - a 32-Byte field containing the sha256 of the video submission
- `speed` - the speed of the vehicle in the incident
- `isTest` - if the data submitted is to be flagged as a test for ease of deletion later
- `time` - the Date and Time of the incident
- `location` - the location of the incident - stored as a JSON of latitude and longitude

To create the required structure, perform the following when connected to the database:

```SQL
-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: mysql.internal.srcf.net:3306
-- Generation Time: Mar 11, 2025 at 02:46 PM
-- Server version: 8.0.41-0ubuntu0.20.04.1
-- PHP Version: 7.4.3-4ubuntu2.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cstdeliveryradar`
--

-- --------------------------------------------------------

--
-- Table structure for table `Incidents`
--
CREATE TABLE `Incidents` (
  `vehicle_id` int NOT NULL,
  `hash` binary(64) NOT NULL,
  `speed` float NOT NULL,
  `isTest` tinyint(1) NOT NULL DEFAULT '0',
  `time` datetime NOT NULL,
  `location` json NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
--
-- Indexes for table `Incidents`
--
ALTER TABLE `Incidents`
  ADD PRIMARY KEY (`vehicle_id`) USING BTREE,
  ADD KEY `hash` (`hash`);

--
-- AUTO_INCREMENT for table `Incidents`
--
ALTER TABLE `Incidents`
  MODIFY `vehicle_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
```

## Secrets

The application requires several configuration settings to be able to run. To setup your own, follow the guide given in [`config.py`](#configpy).