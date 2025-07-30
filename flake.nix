{
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
        flake-utils.url = "github:numtide/flake-utils";
        devkitNix = {
            url = "github:bandithedoge/devkitNix";
            inputs = {
                nixpkgs.follows = "nixpkgs";
                flake-utils.follows = "flake-utils";
            };
        };
    };

    outputs = { self, nixpkgs, flake-utils, devkitNix, ... }:
        flake-utils.lib.eachDefaultSystem (system: let
            pkgs = import nixpkgs {
                inherit system;
                overlays = [devkitNix.overlays.default];
            };
        in {
            devShells.default = pkgs.mkShell.override {stdenv = pkgs.devkitNix.stdenvARM;} {
                buildInputs = with pkgs; [ python313 uv gcc ];
	        };
        }
        );
}
