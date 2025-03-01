{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          DR_FLASK_LOCAL_TEST=1;
          venvDir = ".venv";
          packages = with pkgs; [ python311 nodejs_18 ] ++
            (with pkgs.python311Packages; [
              pip
              venvShellHook
              mysql-connector
              flask
              gunicorn
              numpy
              opencv4
              ( let ultralytics-thop = (buildPythonPackage rec {
                pname = "ultralytics_thop";
                version = "2.0.13";
                src = pkgs.python3Packages.fetchPypi {
                  inherit pname version;
                  sha256 = "afd71619b61aa1d11858d69fff29c1c1e438a1c76bc274e0eaa040548627c384";
                };
                pyproject = true;
                propagatedBuildInputs = with pkgs.python311Packages; [
                  numpy
                  setuptools
                  torch
                ];
                nativeBuildInputs = with pkgs.python311Packages; [
                  setuptools 
                  pip 
                ];
                meta = {
                  description = "Ultralytics";
                  homepage = "https://github.com/ultralytics/ultralytics-thop";
                  license = pkgs.lib.licenses.mit;
                  platforms = pkgs.lib.platforms.all;
                };
              }); in buildPythonPackage rec {
                pname = "ultralytics";
                version = "8.3.61";
                src = pkgs.python3Packages.fetchPypi {
                  inherit pname version;
                  sha256 = "6cbed15f2447ff93d37cafa61f1816ca5bf333bec8b73a2379ea8e87cdc5ccaf";
                };
                pyproject = true;
                propagatedBuildInputs = with pkgs.python311Packages; [
                  requests
                  numpy
                  setuptools
                  matplotlib
                  numpy
                  opencv-python
                  pandas
                  pillow
                  psutil
                  py-cpuinfo
                  pyyaml
                  scipy
                  seaborn
                  torch
                  torchvision
                  tqdm
                  ultralytics-thop
                ];
                preBuild = ''
                  sed -i '/torchvision>=0.9.0/d' pyproject.toml
                '';
                nativeBuildInputs = with pkgs.python311Packages; [
                  setuptools 
                  pip 
                ];
                meta = {
                  description = "Ultralytics";
                  homepage = "https://github.com/ultralytics/ultralytics";
                  license = pkgs.lib.licenses.mit;
                  platforms = pkgs.lib.platforms.all;
                };
              })
            ]) ++ [(
              pkgs.writeScriptBin "load-db-pwd" "export DELIVERYRADAR_DB_PWD=$(cat ./db_pwd)"
            )];
        };
      });
    };
}
