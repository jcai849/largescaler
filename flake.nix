{
  description = "largescaler";

  inputs = {
    utils.url = "github:numtide/flake-utils";

    largescalemodels.url = "github:jcai849/largescalemodels";

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
      utils,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      largescalemodels,
      ...
    }:
    utils.lib.eachDefaultSystem (
      system:
      let
        inherit (nixpkgs) lib;
        pkgs = nixpkgs.legacyPackages.x86_64-linux;

        syspkgs = [
          pkgs.zellij
        ];

        # R Environment

        largescalerr = pkgs.rPackages.buildRPackage {
          name = "largescalemodels";
          version = "1.3";
          src = ./.;
          propagatedBuildInputs = [
            largescalemodels.packages.${system}.default
          ];
        };

        Rpackages = [
          largescalerr
          pkgs.rPackages.languageserver
        ];

        R = pkgs.rWrapper.override { packages = Rpackages; };
        radian = pkgs.radianWrapper.override { packages = Rpackages; };
        radian_exec = pkgs.writeShellApplication {
          name = "r";
          runtimeInputs = [ radian ];
          text = "exec radian";
        };

        # Python Environment
        # don't try understand, this is really trial and error...

        python = pkgs.python313;
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./largescaler; };
        pyprojectOverrides = final: prev: {
          fire = prev.fire.overrideAttrs (old: {
            nativeBuildInputs = old.nativeBuildInputs ++ [ (final.resolveBuildSystem { setuptools = [ ]; }) ];
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
            (final: prev: {
              largescaler = prev.largescaler.overrideAttrs (old: {
                nativeBuildInputs =
                  old.nativeBuildInputs
                  ++ final.resolveBuildSystem {
                    editables = [ ];
                  };
              });
            })
          ]
        );
        largescaler-dev = editablePythonSet.mkVirtualEnv "largescaler-dev-env" workspace.deps.all;

        # Container

        container = pkgs.dockerTools.buildImage {
          name = "largescaler";
          tag = "latest";
          copyToRoot = pkgs.buildEnv {
            name = "image-root";
            paths = [
              pkgs.coreutils-full
              pkgs.bash
              R
              radian
              largescaler
            ] ++ syspkgs;
          };
          extraCommands = "mkdir tmp";
          config = {
            Cmd = [ "bash" ];
          };
        };

      in
      {
        packages.default = container;

        devShells.default = pkgs.mkShell {
          buildInputs =
            with pkgs;
            [
              clang
              clang-tools
              R
              radian
              radian_exec
              pkgs.uv
              largescaler-dev
            ]
            ++ syspkgs;
          env = {
            UV_NO_SYNC = "1";
            UV_PYTHON = "${largescaler-dev}/bin/python";
            UV_PYTHON_DOWNLOADS = "never";
          };

          shellHook = ''
            unset PYTHONPATH
            export REPO_ROOT=$(git rev-parse --show-toplevel)/largescaler
          '';

        };
      }
    );
}
