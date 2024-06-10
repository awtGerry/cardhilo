{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
      /* opencvGtk = opencv.override (old: {
        # enableGStreamer = true;
        enableGtk2 = true;
        # enableGTK3 = true;
      }); */
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          venvDir = "venv";
          packages = with pkgs; [ python311 ] ++
            (with pkgs.python311Packages; [ 
              pip
              (opencv4.override {enableGtk3 = true;})
              requests
              pillow
              zlib
              libGL
              glib
            ]);
        };
        # add path
        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.zlib}/lib:${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.libGL}/lib:${pkgs.glib.out}/lib:/run/opengl-driver/lib"
        '';
      });
    };
}
  # LD_LIBRARY_PATH = "${pin.pkgs.zlib}/lib:${pin.pkgs.stdenv.cc.cc.lib}/lib:${pin.pkgs.libGL}/lib:${pin.pkgs.glib.out}/lib:/run/opengl-driver/lib";
