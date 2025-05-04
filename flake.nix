{
  description = "largescaler";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
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
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      pkgs = nixpkgs.legacyPackages.x86_64-linux;

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

      python = pkgs.python313;
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./largescaler; };
      pyprojectOverrides = final: prev: {
        fire = prev.fire.overrideAttrs (old: {

          # buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.zeromq ];

          # uv.lock does not contain build-system metadata.
          # Meaning that for source builds, this needs to be provided by overriding.
          nativeBuildInputs = old.nativeBuildInputs ++ [
            (final.resolveBuildSystem {
              setuptools = [ ];
            })
          ];

        });
      };

      pythonSet =
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
              pyprojectOverrides
            ]
          );
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };
      largescaler = pythonSet.mkVirtualEnv "largescaler-env" workspace.deps.default;

      editableOverlay = workspace.mkEditablePyprojectOverlay {
        root = "$REPO_ROOT";
      };
      editablePythonSet = pythonSet.overrideScope (
        lib.composeManyExtensions [
          editableOverlay

          # Apply fixups for building an editable package of your workspace packages
          (final: prev: {
            largescaler = prev.largescaler.overrideAttrs (old: {
              # It's a good idea to filter the sources going into an editable build
              # so the editable package doesn't have to be rebuilt on every change.
              src = lib.fileset.toSource {
                root = old.src;
                fileset = lib.fileset.unions [
                  (old.src + "/pyproject.toml")
                  (old.src + "/README.md")
                  (old.src + "/largescaler/__init__.py")
                ];
              };

              # Hatchling (our build system) has a dependency on the `editables` package when building editables.
              #
              # In normal Python flows this dependency is dynamically handled, and doesn't need to be explicitly declared.
              # This behaviour is documented in PEP-660.
              #
              # With Nix the dependency needs to be explicitly declared.
              nativeBuildInputs =
                old.nativeBuildInputs
                ++ final.resolveBuildSystem {
                  editables = [ ];
                  setuptools = [ ];
                };
            });

          })
        ]
      );
      virtualenv = editablePythonSet.mkVirtualEnv "largescaler-dev-env" workspace.deps.all;

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
      packages.x86_64-linux.default = container;

      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          clang
          clang-tools
          zellij
          devREnv
          pkgs.uv
          virtualenv
        ];
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = "${virtualenv}/bin/python";
          UV_PYTHON_DOWNLOADS = "never";
        };

        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
        '';

      };
    };
}
