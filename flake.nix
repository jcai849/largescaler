{
  description = "largescaler";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    self.submodules = true;
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:

      let
        pkgs = nixpkgs.legacyPackages.${system};

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

        Rpackages = [
          orcv
          chunknet
          largescaleobjects
          largescalemodels
        ];

        prodREnv = pkgs.rWrapper.override { packages = Rpackages; };
        devREnv = pkgs.rWrapper.override { packages = Rpackages ++ [ pkgs.rPackages.languageserver ]; };

        baseImage = pkgs.dockerTools.pullImage {
          imageName = "ubuntu";
          imageDigest = "sha256:1e622c5f073b4f6bfad6632f2616c7f59ef256e96fe78bf6a595d1dc4376ac02";
          sha256 = "sha256-qhsqlZVffA2oEF1xYJ4PvTa7F1rJXzaJAfuN0RQBZLc=";
          finalImageName = "ubuntu";
          finalImageTag = "noble";
        };

        container = pkgs.dockerTools.buildImage {
          name = "largescaler";
          tag = "latest";
          fromImage = baseImage;
          copyToRoot = pkgs.buildEnv {
            name = "image-root";
            paths = [
              pkgs.openssh
              pkgs.zellij
              pkgs.bash
              prodREnv
            ];
            pathsToLink = [
              "/bin"
              "/lib"
              "/share"
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
          buildInputs = with pkgs; [
            devREnv
            clang
            clang-tools
            zellij
          ];
        };
      }
    );
}
