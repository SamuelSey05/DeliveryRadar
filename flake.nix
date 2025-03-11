{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      fhs = pkgs.buildFHSEnv {
        name = "fhs-shell";
        targetPkgs = pkgs: with pkgs; [ 
          gcc 
          libtool 
          nodejs_18 
          libGL
          glibc
          glib
          (pkgs.python311.withPackages(ps: with ps; [
            pip
            setuptools
            venvShellHook
          ]))
        ];
        runScript = 
        ''
        $(if [ ! -d .venv ]; then 
          python -m venv .venv 
          source .venv/bin/activate 
          pip install -r requirements.txt
          bash 
        else 
          source .venv/bin/activate
          bash
        fi)
        '';
      };
    in
      {
        devShells.${system}.default = fhs.env;
      };
}