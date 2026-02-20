//UDMv3.4.1
//**DO NOT EDIT THIS *****
if (!exclude) { //********
//************************



///////////////////////////////////////////////////////////////////////////
//
//  ULTIMATE DROPDOWN MENU VERSION 3.5 by Brothercake
//  http://www.brothercake.com/dropdown/ 
//
//  Link-wrapping routine by Brendan Armstrong
//  KDE modifications by David Joham
//  Opera reload/resize routine by Michael Wallner
//  http://www.wallner-software.com/
//
//  This script featured on Dynamic Drive (http://www.dynamicdrive.com)
///////////////////////////////////////////////////////////////////////////



// *** POSITIONING AND STYLES *********************************************



var menuALIGN = "center";		// alignment
var absLEFT = 	0;		// absolute left or right position (if menu is left or right aligned)
var absTOP = 	0; 		// absolute top position

var staticMENU = false;		// static positioning mode (ie5,ie6 and ns4 only)

var stretchMENU = true;		// show empty cells
var showBORDERS = true;		// show empty cell borders

var baseHREF = "";		// base path to .js files for the script (ie: resources/)
var zORDER = 	1000;		// base z-order of nav structure (not ns4)

var mCOLOR = 	"black";	// main nav cell color
var rCOLOR = 	"black";	// main nav cell rollover color
var bSIZE = 	1;		// main nav border size
var bCOLOR = 	"black"		// main nav border color
var aLINK = 	"white";	// main nav link color
var aHOVER = 	"6699CC";		// main nav link hover-color (dual purpose)
var aDEC = 	"none";		// main nav link decoration
var fFONT = 	"mistral";	// main nav font face
var fSIZE = 	18;		// main nav font size (pixels)
var fWEIGHT = 	"bold"		// main nav font weight
var tINDENT = 	7;		// main nav text indent (if text is left or right aligned)
var vPADDING = 	7;		// main nav vertical cell padding
var vtOFFSET = 	0;		// main nav vertical text offset (+/- pixels from middle)

var keepLIT =	true;		// keep rollover color when browsing menu
var vOFFSET = 	5;		// shift the submenus vertically
var hOFFSET = 	4;		// shift the submenus horizontally

var smCOLOR = 	"black";	// submenu cell color

var srCOLOR = 	"black";	// submenu cell rollover color
var sbSIZE = 	1;		// submenu border size
var sbCOLOR = 	"black"	// submenu border color
var saLINK = 	"white";	// submenu link color
var saHOVER = 	"6699CC";		// submenu link hover-color (dual purpose)
var saDEC = 	"none";		// submenu link decoration
var sfFONT = 	"verdana";// submenu font face
var sfSIZE = 	13;		// submenu font size (pixels)
var sfWEIGHT = 	"bold"	// submenu font weight
var stINDENT = 	5;		// submenu text indent (if text is left or right aligned)
var svPADDING = 1;		// submenu vertical cell padding
var svtOFFSET = 0;		// submenu vertical text offset (+/- pixels from middle)

var shSIZE =	2;		// submenu drop shadow size
var shCOLOR =	"FFFFE5";	// submenu drop shadow color
var shOPACITY = 75;		// submenu drop shadow opacity (not ie4,ns4 or opera)

var keepSubLIT = true;		// keep submenu rollover color when browsing child menu
var chvOFFSET = -12;		// shift the child menus vertically
var chhOFFSET = 7;		// shift the child menus horizontally

var closeTIMER = 200;		// menu closing delay time

var cellCLICK = true;		// links activate on TD click
var aCURSOR = "hand";		// cursor for active links (not ns4 or opera)

var altDISPLAY = "";		// where to display alt text
var allowRESIZE = true;		// allow resize/reload

var redGRID = false;		// show a red grid
var gridWIDTH = 0;		// override grid width
var gridHEIGHT = 0;		// override grid height
var documentWIDTH = 0;		// override document width

var hideSELECT = true;		// auto-hide select boxes when menus open (ie only)
var allowForSCALING = false;	// allow for text scaling in mozilla 5


//** LINKS ***********************************************************




// add main link item ("url","Link name",width,"text-alignment","_target","alt text",top position,left position,"key trigger")
addMainItem("http://www.outsidetheworld.com/","Outside the World<span class='u'></span>",201,"center","","",0,0,"e");

	// define submenu properties (width,"align to edge","text-alignment",v offset,h offset,"filter")
	defineSubmenuProperties(190,"left","left",-4,0,"");

	// add submenu link items ("url","Link name","_target","alt text")
	addSubmenuItem("http://www.outsidetheworld.com/wedge.htm","Weekly Blog","","");
	addSubmenuItem("http://www.outsidetheworld.com/archive.htmpage.htm","Wedge Archives","","");
	addSubmenuItem("http://www.outsidetheworld.com/mediapage.htm","Media","","");
	addSubmenuItem("http://www.outsidetheworld.com/writingspage.htm","Writings","","");
	addSubmenuItem("http://www.outsidetheworld.com/linkpage.htm","Links","","");
	addSubmenuItem("http://www.outsidetheworld.com/about.htm","About Me","","");
	addSubmenuItem("mailto:ryan.david@cox.net","Contact Me","","");


addMainItem("","<span class='u'>D</span>ifference of Opinion",198,"center","","",0,0,"w");

	defineSubmenuProperties(190,"left","left",-4,0,"");

	addSubmenuItem("http://www.outsidetheworld.com/~dop/","Main Page","_blank","");
	addSubmenuItem("http://www.outsidetheworld.com/~dop/rants.html","Rants","","");
	addSubmenuItem("http://www.outsidetheworld.com/~dop/readlist.html","Read List","_blank","");
	addSubmenuItem("http://www.outsidetheworld.com/~dop/index.html#news","Latest Updates","_blank","");
	addSubmenuItem("http://www.outsidetheworld.com/~dop/archives.html","Archives","_blank","");


addMainItem("","Ringletin<span class='u'>g</span>",198,"center","","",0,0,"s");

	defineSubmenuProperties(190,"left","left",-4,0,"");

	addSubmenuItem("http://www.outsidetheworld.com/~conjunct/","Main Page","_blank","");
	addSubmenuItem("http://www.outsidetheworld.com/~conjuct/","Latest Updates","_blank","");
	addSubmenuItem("http://www.outsidetheworld.com/~conjunct/","Archives","_blank","");
	

addMainItem("","<span class='u'>B</span>e Gone",198,"center","","",0,0,"t");

	defineSubmenuProperties(190,"left","left",-4,0,"");
	addSubmenuItem("http://www.lileks.com/","James Lileks","","");
	addSubmenuItem("http://www.blogger.com/","Blogger","","");
	addSubmenuItem("http://www.cox.com/","Cox","","");
	addSubmenuItem("http://www.theforce.net/","The Force","","");
	addSubmenuItem("http://www.newyorknorth.com/","New York Mission","","");
	addSubmenuItem("http://www.cnet.com","Cnet","","");
	addSubmenuItem("http://www.msnbc.com","MSNBC","","");


addMainItem("","The Tech Desk <span class='u'></span>",200,"center","","",0,0,"r");

	defineSubmenuProperties(190,"left","left",-4,0,"");

	addSubmenuItem("http://www.tech-desk.net","Main Page","_blank","");
	addSubmenuItem("http://www.tech-desk.net/news.html","News","","");
	addSubmenuItem("http://www.tech-desk.net/reviews.html","Reviews","","");
	addSubmenuItem("http://www.tech-desk.net/http://outsidetheworld.com/blogl","Thoughts","","");
	addSubmenuItem("http://www.tech-desk.net/forum","Forums","","");


//**DO NOT EDIT THIS *****
}//***********************
//************************
