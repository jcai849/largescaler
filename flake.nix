{
  description = "R Dev Container with SSH and Local Packages";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    self.submodules = true;
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        rPackages = with pkgs.rPackages; [
          languageserver
        ];

        orcv = pkgs.rPackages.buildRPackage {
          name = "orcv";
          version = "1.1";
          src = ./orcv;
        };

        chunknet = pkgs.rPackages.buildRPackage {
          name = "chunknet";
          version = "1.1";
          src = ./chunknet;
          propagatedBuildInputs = [
            orcv
            pkgs.rPackages.uuid
          ];
        };

        largescaleobjects = pkgs.rPackages.buildRPackage {
          name = "largescaleobjects";
          version = "1.0";
          src = ./largescaleobjects;
          propagatedBuildInputs = [
            chunknet
            pkgs.rPackages.iotools
            pkgs.rPackages.dplyr
          ];
        };

        largescalemodels = pkgs.rPackages.buildRPackage {
          name = "largescalemodels";
          version = "1.3";
          src = ./largescalemodels;
          propagatedBuildInputs = [
            largescaleobjects
            pkgs.rPackages.biglm
          ];
        };

        localRPackages = [
          orcv
          chunknet
          largescaleobjects
          largescalemodels
        ];

        allRPackages = rPackages ++ localRPackages;

        REnv = pkgs.rWrapper.override { packages = allRPackages; };

        container = pkgs.dockerTools.buildImage {
          name = "largescaler";
          tag = "latest";
          copyToRoot = pkgs.buildEnv {
            name = "image-root";
            paths = [
              REnv
              pkgs.openssh
              pkgs.zellij
            ];
          };
          config = {
            Cmd = [ "bash" ];
          };
        };

      in
      {
        packages.default = container;

        devShells.default = pkgs.mkShell {
          buildInputs = [
            REnv
            pkgs.zellij
            pkgs.openssh
          ];
        };
      }
    );
}
