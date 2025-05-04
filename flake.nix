{
  description = "largescaler";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    self.submodules = true;
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,

      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:

      let
        pkgs = nixpkgs.legacyPackages.${system};

        # R Environment

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

        # Python Environment

        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./largescaler; };

        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel"; # or sourcePreference = "sdist";
        };
        python = pkgs.python313;
        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              pkgs.lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
              ]
            );
        largescaler = pythonSet.mkVirtualEnv "largescaler-env" workspace.deps.default;

        # Container

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
              largescaler
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

        devShells.default =
          let
            largescaler-dev-venv = pythonSet.mkVirtualEnv "largescaler-dev-env" workspace.deps.all;
          in
          pkgs.mkShell {
            buildInputs = with pkgs; [
              clang
              clang-tools
              zellij
              devREnv
              largescaler-dev-venv
              pkgs.uv
            ];
            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = "${largescaler-dev-venv}/bin/python";
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
            '';

          };
      }
    );
}
