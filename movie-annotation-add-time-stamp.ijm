setForegroundColor(255, 255, 255);
setFont("Arial", 20, "antiliased");

// DLD-1-spheroids phase contrast and epifluorescence movie
// 20-font size, top right for 1030 width images
//setForegroundColor(0, 0, 0);
//run("Time Stamper", "starting=0 interval=0.25 x=960 y=27 font=20 decimal=1 anti-aliased or=[h]");

//// 191013-DLD-1-spheroids-movie
//// 20-font size, top right for 925 width images
//run("Time Stamper", "starting=0 interval=0.166667 x=855 y=27 font=20 decimal=1 anti-aliased or=[h]");
//
//// label transgene markers on the top left part next to the inset
setForegroundColor(0, 255, 0);
setFont("Arial", 20, "antiliased");
run("Time Stamper", "starting=0 interval=0 x=5 y=27 font=20 decimal=0 anti-aliased or=[NLS-mNeonGreen (sg-Control)]");
//setForegroundColor(255, 0, 255);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=358 y=52 font=20 decimal=0 anti-aliased or=[NLS-mScarlet (sg2-Cdh1)]");
//setForegroundColor(255, 255, 0);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=358 y=77 font=20 decimal=0 anti-aliased or=[Basement membrane]");

// 20-font size, top right for 1024 width images
//run("Time Stamper", "starting=0 interval=0.166667 x=954 y=27 font=20 decimal=1 anti-aliased or=[h]");

// 2020-01-25-4 SMG 3D reconstruction
// label transgene markers on the top left part
//setForegroundColor(0, 255, 0);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=27 font=20 decimal=0 anti-aliased or=[Native KikGR]");
//setForegroundColor(255, 0, 255);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=52 font=20 decimal=0 anti-aliased or=[Photoconverted KikGR]");

//// label collangen IV antibody marker on the top left part of the right panel
//setForegroundColor(255, 255, 0);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=517 y=27 font=20 decimal=0 anti-aliased or=[AF680-anti-Collagen IV]");

//run("Time Stamper", "starting=0 interval=0.0833 x=1200 y=30 font=20 decimal=1 anti-aliased or=[h]");

// 20-font size, top right for 640 width images
//run("Time Stamper", "starting=0 interval=0.0833 x=570 y=27 font=20 decimal=1 anti-aliased or=[h]");


// top left for any size images
//run("Time Stamper", "starting=0 interval=0.0833 x=5 y=32 font=25 decimal=1 anti-aliased or=[h]");

// top right for 640 width images
//run("Time Stamper", "starting=0 interval=0.0833 x=555 y=32 font=25 decimal=1 anti-aliased or=[h]");


// 2020-01-25-4 SMG 3D reconstruction
// label transgene markers on the middle left portion (640x720)
//setForegroundColor(255, 0, 255);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=30 font=20 decimal=0 anti-aliased or=[Krt14p::RFP]");
//setForegroundColor(0, 255, 0);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=53 font=20 decimal=0 anti-aliased or=[Histone-EGFP]");


// 180218 set, resliced images, left justification
//run("Time Stamper", "starting=329 interval=0 x=5 y=25 font=20 decimal=0 anti-aliased or=[t: 0.0h]");
////run("Time Stamper", "starting=329 interval=0 x=5 y=25 font=20 decimal=0 anti-aliased or=[t: 12.4h]");
//run("Time Stamper", "starting=329 interval=0 x=5 y=48 font=20 decimal=0 anti-aliased or=[x: ]");
//run("Time Stamper", "starting=329 interval=4 x=29 y=48 font=20 decimal=0 anti-aliased or=[um]");
//run("Time Stamper", "starting=329 interval=0 x=5 y=71 font=20 decimal=0 anti-aliased or=[y-z plane]");

// 180218 set, resliced images, right justification
//run("Time Stamper", "starting=329 interval=0 x=54 y=25 font=20 decimal=0 anti-aliased or=[t: 0.0h]");
////run("Time Stamper", "starting=329 interval=0 x=41 y=25 font=20 decimal=0 anti-aliased or=[t: 12.4h]");
//run("Time Stamper", "starting=329 interval=0 x=18 y=48 font=20 decimal=0 anti-aliased or=[x: ]");
//run("Time Stamper", "starting=329 interval=4 x=42 y=48 font=20 decimal=0 anti-aliased or=[um]");
//run("Time Stamper", "starting=329 interval=0 x=25 y=71 font=20 decimal=0 anti-aliased or=[y-z plane]");

//// 180218 set, combined time lapse part
//run("Time Stamper", "starting=0 interval=0 x=5 y=25 font=20 decimal=0 anti-aliased or=[3D view]");
//run("Time Stamper", "starting=0 interval=0 x=1105 y=25 font=20 decimal=0 anti-aliased or=[t:]");
//run("Time Stamper", "starting=0 interval=0.0833 x=1125 y=25 font=20 decimal=1 anti-aliased or=h");
//// label what view this one is:
//run("Time Stamper", "starting=0 interval=0 x=1021 y=48 font=20 decimal=0 anti-aliased or=[x-y middle plane]");
//// label transgene markers on the top right corner under time stamp
//setForegroundColor(255, 0, 255);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=980 y=71 font=20 decimal=0 anti-aliased or=[Membrane-tdTomato]");
//setForegroundColor(0, 255, 0);
//setFont("Arial", 20, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=1054 y=94 font=20 decimal=0 anti-aliased or=[Histone-EGFP]");



// 190227 set, label transgene markers on the top left corner
//
//setForegroundColor(255, 0, 255);
//setFont("Arial", 25, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=32 font=25 decimal=0 anti-aliased or=[Membrane-tdTomato]");
//
//setForegroundColor(0, 255, 0);
//setFont("Arial", 25, "antiliased");
//run("Time Stamper", "starting=0 interval=0 x=5 y=60 font=25 decimal=0 anti-aliased or=[Histone-EGFP]");


//run("Time Stamper", "starting=0 interval=0.0833 x=5 y=32 font=25 decimal=1 anti-aliased or=[h]");

//// Note: when font size is 24 and y position <= 28 points, the anti-aliased is automatically turned off
//// Probably some bug about anti-aliased on handling the distance to edge
//run("Time Stamper", "starting=0 interval=5 x=28 y=198 font=18 decimal=0 anti-aliased or=min");
//run("Time Stamper", "starting=0 interval=1 x=110 y=198 font=18 decimal=0 anti-aliased or=um(z)");

//// 1-digit to center
//run("Time Stamper", "starting=0 interval=0 x=35 y=23 font=18 decimal=0 anti-aliased or=[cell division 8b]");
//// 2-digits to center
//run("Time Stamper", "starting=0 interval=0 x=30 y=23 font=18 decimal=0 anti-aliased or=[cell division 16b]");


//run("Rotate 90 Degrees Right");
//run("Rotate 90 Degrees Left");


//// Add time stamp to near-final tif series for movies; 0.0833 is approximation for 1/12 h (5 min)
//setFont("Arial", 30, "antiliased");
//run("Time Stamper", "starting=0 interval=0.0833 x=6 y=36 font=30 decimal=1 anti-aliased or=h");
