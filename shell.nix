with import <nixpkgs> {};
(

let python =
    let
    packageOverrides = self:
    super: {
      opencv4 = super.opencv4.override {
        enableGtk2 = true;
        gtk2 = pkgs.gtk2;
        enableFfmpeg = true; #here is how to add ffmpeg and other compilation flags
        };
    };
    in
      pkgs.python38.override {inherit packageOverrides; self = python;};

in

stdenv.mkDerivation {
  name = "impurePythonEnv";
  buildInputs = [
    imagemagick
    v4l-utils
    (python38.buildEnv.override {
      extraLibs = [
	pkgs.python38Packages.matplotlib
	pkgs.python38Packages.numpy
	pkgs.python38Packages.scipy
	pkgs.python38Packages.gnureadline        
        python.pkgs.opencv4
      ];
      ignoreCollisions = true;
    })
  ];
  shellHook = ''
        # set SOURCE_DATE_EPOCH so that we can use python wheels
        SOURCE_DATE_EPOCH=$(date +%s)
        export LANG=en_US.UTF-8	
  '';
})
