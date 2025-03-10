# DeliveryRadar

## Project Summary

## Running the Application

### Basics

<!-- TODO: setup instructions -->

To run the application for testing, clone the repo and setup secrets, then run the command `flask run` from the project root. This will open up a server listening on [localhost:5000](https://localhost:5000).

### Deployment

<!-- TODO -->

#### Pyenv

<!-- TODO -->

#### NVM

<!-- TODO -->

#### Creating a Venv

<!-- TODO -->

#### Gunicorn

<!-- TODO -->

#### SystemD

<!-- TODO -->

### Options and Environment Variables

#### `secrets.py`

<!-- TODO - actually have a secrets.py -->

#### `DR_FLASK_LOCAL_TEST`

<!-- TODO -->

#### `DR_TEST_SCHED`

<!-- TODO -->

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

<!-- TODO: Update requirements.txt - Depends on having a working flake -->
```bash
pip install -r requirements.txt
```
  
Additionally, the website frontend is written in React.js, using Node version 18. To install it's dependencies, perform the following commands from the root directory:

```Bash
cd videoUpload
npm install
```

## Database

<!-- TODO -->

## Secrets

<!-- TODO -->