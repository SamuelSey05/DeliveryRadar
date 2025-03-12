{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell{
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
            stdenv
            stdenv.cc.cc.lib
            glib
            libGL
          ]);
          venvDir = ".venv";
          packages = (with pkgs; [
            python311
            nodejs_18
          ]) ++ (with pkgs.python311Packages; [
            pip
            venvShellHook
            setuptools
          ]);

          # Set Environment Variables for app
          DR_FLASK_LOCAL_TEST=1;
          TMPDIR="/tmp";
        };
      });
    };
}