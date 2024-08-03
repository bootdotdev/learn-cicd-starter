{ pkgs ? import <nixpkgs> {} }:
    pkgs.mkShell {
      # nativeBuildInputs is usually what you want -- tools you need to run
      nativeBuildInputs = with pkgs.buildPackages; [ 
        libgcc
        pkg-config
        go
        openssl 
        ];
        PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig";
  }
