{
  description = "";

  # Flake inputs
  inputs = {
    # Latest stable Nixpkgs
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0";
  };

  # Flake outputs
  outputs =
    { self, nixpkgs }:
    let
      # Systems supported
      allSystems = [
        "x86_64-linux" # 64-bit Intel/AMD Linux
        "aarch64-linux" # 64-bit ARM Linux
        "x86_64-darwin" # 64-bit Intel macOS
        "aarch64-darwin" # 64-bit ARM macOS
      ];

      # Helper to provide system-specific attributes
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs allSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      # Development environment output
      devShells = forAllSystems (
        { pkgs }:
        {
          default =
            let
              bootdev = pkgs.buildGoModule {
                pname = "bootdev";
                version = "af37236b46b92cecd81a6a0d83847ae5b2e70f58";

                src = pkgs.fetchFromGitHub {
                  owner = "bootdotdev";
                  repo = "bootdev";
                  rev = "af37236b46b92cecd81a6a0d83847ae5b2e70f58";
                  # sha256 = pkgs.lib.fakeHash;
                  sha256 = "sha256-ZNQ2B7C36lHL7B43aKexCg2AcRAgFHU+gYphmGfmOvw=";
                };

                 # vendorHash = pkgs.lib.fakeHash;
                 vendorHash = "sha256-jhRoPXgfntDauInD+F7koCaJlX4XDj+jQSe/uEEYIMM=";
              };
            in
            pkgs.mkShell {
              # The Nix packages provided in the environment
              packages = [
                bootdev
                pkgs.go
                pkgs.gopls
                pkgs.gotools
                pkgs.gofumpt
                pkgs.golangci-lint
              ];
              shellHook = ''
                exec fish
              '';
            };
        }
      );
    };
}
