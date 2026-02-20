//UDMv3.4.1



// filter for undefined arrays
for (var f=0;f<mI.length;f++){
if(typeof sP[f]=="undefined"){sP[f]=new Array(mI[f][2],mI[f][3],mI[f][3],0,0);}
if(typeof cP[f]=="undefined"){cP[f]=new Array;}
if(typeof sI[f]=="undefined"){sI[f]=new Array;}
if(typeof cI[f]=="undefined"){cI[f]=new Array;}
for (var sf=0;sf<sI[f].length;sf++){
if(typeof cP[f][sf]=="undefined"){cP[f][sf]=new Array;}
if(typeof cI[f][sf]=="undefined"){cI[f][sf]=new Array;}
}}

// set undefined or disallowed values
if(absTOP<0){absTOP=0;}
if(absLEFT<0){absLEFT=0;}
if(vPADDING<0){vPADDING=0;}
if(svPADDING<0){svPADDING=0;}
if(aHOVER=="") { aHOVER=aLINK; }
if(saHOVER=="") { saHOVER=saLINK; }
if(aCURSOR=="hand"){aCURSOR="pointer";}
if(konqi){allowForSCALING=false;}

//find colors or images
var tempImg;
var bnk=".gif";
var bk=new Array(mCOLOR,bCOLOR,rCOLOR,smCOLOR,sbCOLOR,srCOLOR,shCOLOR);
var bks=new Array;
var ui=new Array(false,false,false,false,false,false);
if(bk[2]=="") { bk[2]=mCOLOR; }
if(bk[5]=="") { bk[5]=bk[3]; }

for (var b=0;b<bk.length;b++){
	if(bk[b]=="") { bk[b]=""; }
	if((bk[b].indexOf('.gif') != -1) || (bk[b].indexOf('.jpg') != -1)){
		ui[b]=true;
		tempImg=bk[b];
		bk[b]=new Image;
		bk[b].src=baseHREF+tempImg;
		bks[b] = 'background-image:url('+bk[b].src+')\;';
		}
	else {
		if(bk[b]=="") { bks[b] = 'background-color:transparent\;';  }
		else { bks[b] = 'background-color:'+bk[b]+'\;';  }
		}
	}
if(ui[2]&&!ui[0]) { bks[0]+='background-image:url('+bnk+')\;'; }
if(ui[0]&&!ui[2]) { bks[2]+='background-image:url('+bnk+')\;'; }
if(ui[5]&&!ui[3]) { bks[3]+='background-image:url('+bnk+')\;'; }
if(ui[3]&&!ui[5]) { bks[5]+='background-image:url('+bnk+')\;'; }




//do nothing
function doNothing(){}



// find the inner width and height of the browser window
var bWidth=window.innerWidth;
var bHeight=window.innerHeight;



// compensate for lack of scrollbar if applicable
var sbaa=14;
if(!konqi){
	if(mac&&mz7){sbaa=16;}
	if(agt.indexOf("rc1")!=-1){sbaa=19;}
	if((mz7&&win&&(agt.indexOf("windows nt 5.1")!=-1))||mac||ns6){if(document.width <= (innerWidth-30)){bWidth-=sbaa;}}
	else if(mz7&&win&&(agt.indexOf("windows nt 5.0")!=-1)){if(document.width <= (innerWidth-16)){bWidth-=16;}}
	else if(win){if(document.width <= (innerWidth-17)){bWidth-=17;}}
	if(lin){if(document.width <= (innerWidth-17)){bWidth-=17;}}
	if(menuALIGN=="free"){bWidth-=sbaa;}
	}


//override width if defined
if(documentWIDTH>0){bWidth=documentWIDTH;}



//set nav height for backward compatibility
var navH=fSIZE+5+vPADDING;
if (fSIZE<13) { navH+=(13-fSIZE); }
var origH=navH;

// find wrapping links routine by brendan armstrong
var Mrows=new Array;var Nrows=new Array;
for(var i=0;i<mI.length;i++){
var thisT=mI[i][1];
var splitT=thisT.split('<br>');
Mrows[i]=splitT.length;
Nrows[i]=Mrows[i];
}
function cFun(a,b) { return b-a; }
Mrows.sort(cFun);
navH=navH*Mrows[0];

var thisNavH=new Array;
for(i=0;i<mI.length;i++){
	if(menuALIGN=="free"){
		thisNavH[i]=origH*Nrows[i];
		}
	else{
		thisNavH[i]=navH;
		}
	}


// find the subnav item height
var subNavH=sfSIZE+5+svPADDING;
if (sfSIZE<13) { subNavH+=(13-sfSIZE); }


//calculate nav width
var endSpace=0;
var navSpace=0;
for (var j=0;j<mI.length;j++){
	if(mI[j][2]==""){mI[j][2]=10;}
	if(mI[j][1]==""){mI[j][1]='&nbsp;';}
	navSpace+=mI[j][2]+bSIZE;
	}
navSpace+=bSIZE;
endSpace=bWidth-navSpace;



//set values for different alignments
var ra=false;
if(menuALIGN=="right"){
ra=true;
absLEFT=endSpace-absLEFT;
}

var ca=false;
if(menuALIGN=="center"){
ca=true;
absLEFT=endSpace / 2;
}

var la=false;
if(menuALIGN=="left"){
la=true;
}


//if(navSpace>bWidth&&menuALIGN!="free") { absLEFT=0; }

//convert shadow type
var shy=0;
var shType;
if(typeof shSIZE == "number") {
	if(shSIZE<0){shSIZE=0;}
	shy-=shSIZE;
	shType="number";
	}
if(typeof shSIZE == "string") {
	shSIZE=parseInt(shSIZE);
	shy+=shSIZE;
	shType="string";
	}

//variables
var tInfo,titleText,master,nav,grid,pObj,nObj,ncObj,sObj,snObj,scObj,cObj,cnObj,ccObj,sNode,temSNode,temCNode,shObj,sLeft,slMargin,srMargin,sTop,stMargin,mSize,mNumOf,cNode,cshObj,cLeft,clMargin,crMargin,cTop,ctMargin,cmSize,cNumOf;

//show grid
var grs;
function showGrid() {
	grs=grid.style.visibility;
	if(grs=="hidden"){grid.style.visibility="visible";}
	}
//hide grid
function hideGrid() {
	grs=grid.style.visibility;
	if(grs=="visible"){grid.style.visibility="hidden";}
	}


// write status message
function writeStatus(sTxt){
	window.status=sTxt;
	return true;
	}


// clear child menus
function clearChildMenus() {

	cNumOf = cObj.childNodes.length;
	for(i=0;i<cNumOf;i++){
		cObj.removeChild(cObj.childNodes[i]);
		}

	currentID = [currentID[0],-1,-1];
	}




// actually clear submenus
var currentID = [-1,-1,-1];
var previousID = [-1,-1,-1];
var focusID = [-1,-1,-1];
var cTimer=0;
var closeOkay=false;
var fid=0;
function clearSubMenus() {

	if(currentID[0]>-1) {
		for(i=0;i<mI.length;i++){
			ncObj = document.getElementById("maincell-"+i);
			ncObj.style.zIndex = zORDER+3;
			}
		ncObj = document.getElementById("maincell-"+currentID[0]);
		if(typeof ncObj != "undefined") {
			if(ui[2]) {
				if(ui[0]) { ncObj.style.backgroundImage = 'url('+bk[0].src+')'; }
				else { ncObj.style.backgroundImage = 'url('+bnk+')'; }
				}
			else {
				if(ui[0]) { ncObj.style.backgroundImage = 'url('+bk[0].src+')'; }
				else { ncObj.style.backgroundColor = bk[0]; }
				}
			ncObj.firstChild.firstChild.firstChild.firstChild.firstChild.style.color = aLINK;
			}

		mNumOf = sObj.childNodes.length;
		for(i=0;i<mNumOf;i++){
			sObj.removeChild(sObj.childNodes[i]);
			}

		clearChildMenus();
		}

	writeStatus('');

	currentID = [-1,-1,-1];
	focusID=[-1,-1,-1];

	hideGrid();
	clearTimeout(cTimer);
	closeOkay=false;
	}



// start clear menus from grid
function gridClearMenus() {

	if(closeOkay) {
		clearTimeout(cTimer);
		clearSubMenus();
		}
	else {
		closeOkay=true;
		cTimer=setTimeout("gridClearMenus()",closeTIMER);
		}

	}


// td click handlers
var wins = new Array;
var wNum = 0;
function goToUrl(cUrl,cTarg){
	if(cUrl.indexOf("mailto:")!=-1){ document.location=cUrl; }
	else if(cUrl!=""){
		if(cTarg=="_self"){self.document.location=cUrl;}
		else if(cTarg=="_top"){top.document.location=cUrl;}
		else if(cTarg=="_parent"){parent.document.location=cUrl;}
		else if(cTarg=="_blank"){
			wins[wNum]=open(cUrl,"","status=yes,scrollbars=yes,scrolling=yes,toolbar=yes,menubar=yes,location=yes,resizable=yes");
			wNum++;
			}
		else {
			if(top[cTarg]){top[cTarg].document.location=cUrl}
			else {document.location=cUrl;}
			}
		}
	}


//main cell rollover
function mainRollover(rmNum) {

	for(i=0;i<mI.length;i++){
		ncObj = document.getElementById("maincell-"+i);
		ncObj.style.zIndex = zORDER+20;
		}
	ncObj = document.getElementById("maincell-"+rmNum);

	if(ui[2]) {
		ncObj.style.backgroundImage = 'url('+bk[2].src+')';
		}
	else {
		ncObj.style.backgroundImage = 'url('+bnk+')';
		ncObj.style.backgroundColor = bk[2];
		}
	ncObj.firstChild.firstChild.firstChild.firstChild.firstChild.style.color = aHOVER;

	if(altDISPLAY=="status") {
		writeStatus(mI[rmNum][5]);
		}
	else {
		tInfo=mI[rmNum][0];
		if(tInfo=="#") { tInfo = ""; }
		writeStatus(tInfo);
		}

	}


//main cell events
var kcc=-1;
var sPlay=false;
var cPlay=false;
function mainCell(mNum,gridTrue) {

	if(typeof mI[mNum]=="undefined") { return false; }

	currentID = previousID;
	clearSubMenus();
	currentID = [mNum,-1,-1];
	previousID = currentID;
	focusID=currentID;

	mainRollover(mNum);

	if(sI[mNum].length>0) { openSubMenu(mNum); }

	if(typeof gridTrue=="undefined") { showGrid(); }
	
	return currentID;
	}

//minimum main cell events
function partialMainCell(mNum) {

	mainRollover(mNum);

	if(sI[mNum].length>0) {
		if(previousID[1]>-1) { clearCell(document.getElementById("subcell-"+mNum+"-"+previousID[1])); }
		}

	}


//open submenu
var sn,stObj,shAry,chAry,swPad,shPad,nodeHtml,mDiff,wAdj,tfObj;
var kPressed=false;

var shopac='-moz-opacity:'+(shOPACITY/100);
if(!win){shopac='';}

var stt,textScale,applyWidth,applyWidthII;
function openSubMenu(mid) {

	//create node
	sNode = document.createElement("div");
	document.getElementById("manch").appendChild(sNode);

	//build submenu items
	sn='';

	applyWidth='width:auto;min-width:'+sP[mid][0]+'px\;white-space:nowrap\;';
	if(konqi){applyWidth='width:'+sP[mid][0]+'px\;';}
	sn+='<div id="subtable-'+mid+'" style="'+applyWidth+'-moz-opacity:1\;position:relative\;left:'+shy+'px\;top:'+shy+'px\;'+bks[4]+'"><table cellpadding=0 cellspacing='+sbSIZE+' border=0>';
	shAry = new Array;
	chAry = new Array;
	for(i=0;i<sI[mid].length;i++){
		sn+='<tr>';
		clcu = '';
		if(cellCLICK&&sI[mid][i][0]!=""&&sI[mid][i][0]!="#"&&sI[mid][i][0]!="~") { clcu = ' cursor:'+aCURSOR+'\;'; }
		cllu=' cursor:default\;';
		if(sI[mid][i][0]!=""&&sI[mid][i][0]!="#"&&sI[mid][i][0]!="~") { cllu = ' cursor:'+aCURSOR+'\;'; }

		// find wrapping links routine by brendan armstrong
		shAry[i]=subNavH;
		var thisT=sI[mid][i][1];
		var splitT=thisT.split('<br>');
		var Trows=splitT.length;
		if (Trows>1) { shAry[i]=(subNavH*Trows)-(svPADDING*(Trows-1)); }

		titleText=""; if(altDISPLAY=="title") { titleText = sI[mid][i][3]; }
		textScale='width:auto;min-width:'+(sP[mid][0]-(2*sbSIZE))+'px\;height:auto;min-';
		if(!allowForSCALING) { textScale='width:'+(sP[mid][0]-(2*sbSIZE))+'px\;'; }
		sn+='<td style="'+clcu+'" align='+sP[mid][2]+'><div title="'+titleText+'" class=SUBmTD onfocus="subCell('+mid+','+i+')" onmouseover="temCNode=document.getElementById(\'childmenu-'+mid+'-'+i+'\')\;if(!temCNode){subCell('+mid+','+i+')}else{partialSubCell('+mid+','+i+')}" onclick="if(cellCLICK){goToUrl(sI['+mid+']['+i+'][0],sI['+mid+']['+i+'][2])}" id="subcell-'+mid+'-'+i+'" style="'+bks[3]+''+textScale+'height:'+shAry[i]+'px\;white-space:nowrap;"><div onmouseout="event.cancelBubble=true" id="subtext-'+mid+'-'+i+'" style="'+cllu+'position:relative"><span style="color:'+saLINK+'\;font:'+sfSIZE+' '+sfFONT+'\;font-weight:'+sfWEIGHT+'\;" onclick="if(!cellCLICK){goToUrl(sI['+mid+']['+i+'][0],sI['+mid+']['+i+'][2])}">'+sI[mid][i][1]+'</span></div></div></td>';
		sn+='</tr>';
		}
	sn+='</table></div>';

	//set position

	sTop = parseInt(ncObj.style.top)+thisNavH[mid];
	if(vOFFSET<0) { sTop+=vOFFSET; } if(sP[mid][3]<0) { sTop+=sP[mid][3]; }

	if(shType=="string") { sTop-=(shSIZE*2); }

	stMargin=bSIZE;
	if(vOFFSET>0) { stMargin+=vOFFSET; }
	if(sP[mid][3]>0) { stMargin+=sP[mid][3]; }

	stMargin+=shSIZE;

	sLeft = parseInt(ncObj.style.left);
	if(shType=="string") { sLeft-=(shSIZE*2); }


	swPad=sbSIZE;shPad=0;
	if(shType=="string") {
		swPad=(2*shSIZE)+sbSIZE;
		shPad=(2*shSIZE);
		}


	slMargin = 0;
	srMargin = 0;
	if(sP[mid][1]=="left") {
		wAdj=false;
		if((parseInt(ncObj.style.top)+thisNavH[mid])>sTop&&(sLeft<(hOFFSET+sP[mid][4]+mI[mid][2]))) { wAdj=true; sLeft+=mI[mid][2]; }
		if(hOFFSET>0) { slMargin+=hOFFSET; }
		if(sP[mid][4]>0) { slMargin+=sP[mid][4]; }
		if(hOFFSET<0) { sLeft+=hOFFSET; }
		if(sP[mid][4]<0) { sLeft+=sP[mid][4]; }
		if(wAdj) {
			if(slMargin>mI[mid][2]) { slMargin-=mI[mid][2]; }
			else { sLeft-=(mI[mid][2]-slMargin); slMargin=0; }
			}
		}
	if(sP[mid][1]=="right") {
		mSize=0;
		if(hOFFSET>0) { srMargin+=hOFFSET; mSize+=srMargin; }
		if(sP[mid][4]>0) { srMargin+=sP[mid][4]; mSize+=srMargin; }
		if(hOFFSET<0) { sLeft-=hOFFSET; }
		if(sP[mid][4]<0) { sLeft-=sP[mid][4]; }
		sLeft-=(sP[mid][0]-mI[mid][2]+mSize);
		}

	slMargin+=shSIZE;


	//write submenu
	applyWidth='width:auto;min-width:'+(sP[mid][0]+slMargin)+'px\;white-space:nowrap\;';
	if(konqi){applyWidth='width:'+(sP[mid][0]+slMargin)+'px\;';}
	applyWidthII='width:auto;min-width:'+(sP[mid][0]+swPad-sbSIZE)+'px\;white-space:nowrap\;';
	if(konqi){applyWidthII='width:'+(sP[mid][0]+swPad-sbSIZE)+'px\;';}
	sNode.parentNode.innerHTML='<div onmouseover="showGrid()" id="submenu-'+mid+'" style="'+applyWidth+'visibility:hidden\;position:absolute\;left:'+sLeft+'px\;top:'+sTop+'px\;z-index:'+(zORDER+40)+'\;"><div id="subshadow-'+mid+'" style="'+shopac+'\;margin-top:'+stMargin+'px\;margin-left:'+slMargin+'px\;margin-right:'+srMargin+'px\;'+bks[6]+'z-index:'+(zORDER+41)+'\;'+applyWidthII+'height:1px\;">'+sn+'</div></div>';

	clearTimeout(cTimer);
	closeOkay=false;
	//position text layers
	for(i=0;i<sI[mid].length;i++){
		stObj=document.getElementById('subtext-'+mid+'-'+i);
		stt=((stObj.parentNode.offsetHeight/2)-(stObj.offsetHeight/2)+svtOFFSET)+"px";
		stObj.style.top = stt;
		if(sP[mid][2]=="left") { stObj.style.left = stINDENT+"px"; }
		if(sP[mid][2]=="right") { stObj.style.left = (0-stINDENT)+"px"; }
		}

	//size dropshadow
	shObj=document.getElementById('subshadow-'+mid);
	shObj.style.height=(document.getElementById('subtable-'+mid).offsetHeight+shPad)+"px";

	//submenu object
	snObj = document.getElementById('submenu-'+mid);

	//show submenu
	if(!remoteTRIGGERING) { snObj.style.visibility="visible"; }

	return snObj;
	}



//clear submenu rollover
function clearSubRollover(rmNum,rsNum) {

	if(!keepLIT) {
		ncObj.firstChild.firstChild.firstChild.firstChild.firstChild.style.color = aLINK;
		if(ui[2]) {
			if(ui[0]) { ncObj.style.backgroundImage = 'url('+bk[0].src+')'; }
			else { ncObj.style.backgroundImage = 'url('+bnk+')'; }
			}
		else {
			if(ui[0]) { ncObj.style.backgroundImage = 'url('+bk[0].src+')'; }
			else { ncObj.style.backgroundColor = bk[0]; }
			}
		}

	if(previousID[1]>-1) {
		pObj = document.getElementById('subcell-'+previousID[0]+'-'+previousID[1]);
		if(ui[5]) {
			if(ui[3]) { pObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { pObj.style.backgroundImage = 'url('+bnk+')'; }
			}
		else {
			if(ui[3]) { pObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { pObj.style.backgroundColor = bk[3]; }
			}
		pObj.firstChild.firstChild.style.color = saLINK;
		}
	}


//submenu rollover
function subRollover(rmNum,rsNum) {

	if(sI[rmNum][rsNum][4]){
		if(ui[5]) {
			scObj.style.backgroundImage = 'url('+bk[5].src+')';
			}
		else {
			scObj.style.backgroundImage = 'url('+bnk+')';
			scObj.style.backgroundColor = bk[5];
			}
		}

	scObj.firstChild.firstChild.style.color = saHOVER;

	if(altDISPLAY=="status") {
		writeStatus(sI[rmNum][rsNum][3]);
		}
	else {
		tInfo=sI[rmNum][rsNum][0];
		if(tInfo=="#") { tInfo = ""; }
		writeStatus(tInfo);
		}

	}



//submenu cell events
var cn,ctObj;
function subCell(mNum,sNum) {

	clearTimeout(cTimer);
	closeOkay=false;

	clearSubRollover();

	currentID = [mNum,sNum,-1];
	previousID = currentID;
	focusID=currentID;
	scObj = document.getElementById('subcell-'+mNum+'-'+sNum);

	subRollover(mNum,sNum);

	openChildMenu(mNum,sNum);

	showGrid();
	}


//minimum sub cell events
function partialSubCell(mNum,sNum) {

	clearSubRollover();
	subRollover(mNum,sNum);

	if(cI[mNum][sNum].length>0) {
		if(previousID[2]>-1) { clearCell(document.getElementById("childcell-"+mNum+"-"+sNum+"-"+previousID[2])); }
		}


	}




//open childmenu
var ctt;
var evcy,evoh,evst,mctPos;
function openChildMenu(mid,cid) {

	clearChildMenus();

	if(cI[mid][cid].length<=0) { return false; }

	//create node
	cNode = document.createElement("div");
	document.getElementById("canch").appendChild(cNode);

	cn = '';
	applyWidth='width:auto;min-width:'+cP[mid][cid][0]+'px\;white-space:nowrap;';
	if(konqi){applyWidth='width:'+cP[mid][cid][0]+'px\;';}
	cn+='<div id="childtable-'+mid+'-'+cid+'" style="'+applyWidth+'-moz-opacity:1\;position:relative\;left:'+shy+'px\;top:'+shy+'px\;'+bks[4]+'"><table cellpadding=0 cellspacing='+sbSIZE+' border=0>';
	chAry[mid] = new Array;
	for(i=0;i<cI[mid][cid].length;i++){
		cn+='<tr>';
		clcu = '';
		if(cellCLICK&&cI[mid][cid][i][0]!=""&&cI[mid][cid][i][0]!="#"&&cI[mid][cid][i][0]!="~") { clcu = ' cursor:'+aCURSOR+'\;'; }
		cllu=' cursor:default\;';
		if(cI[mid][cid][i][0]!=""&&cI[mid][cid][i][0]!="#"&&cI[mid][cid][i][0]!="~") { cllu = ' cursor:'+aCURSOR+'\;'; }

		// find wrapping links routine by brendan armstrong
		chAry[mid][i]=subNavH;
		var thisT=cI[mid][cid][i][1];
		var splitT=thisT.split('<br>');
		var Trows=splitT.length;
		if (Trows>1) { chAry[mid][i]=(subNavH*Trows)-(svPADDING*(Trows-1)); }

		titleText=""; if(altDISPLAY=="title") { titleText = cI[mid][cid][i][3]; }
		textScale='width:auto;min-width:'+(cP[mid][cid][0]-(sbSIZE*2))+'px\;height:auto;min-';
		if(!allowForSCALING){ textScale='width:'+(cP[mid][cid][0]-(sbSIZE*2))+'px\;'; }
		cn+='<td style="'+clcu+'" align='+cP[mid][cid][2]+'><div title="'+titleText+'" class=SUBmTD onfocus="childCell('+mid+','+cid+','+i+')" onblur="clearCell(this)" onmouseover="childCell('+mid+','+cid+','+i+')" onclick="if(cellCLICK){goToUrl(cI['+mid+']['+cid+']['+i+'][0],cI['+mid+']['+cid+']['+i+'][2])}" id="childcell-'+mid+'-'+cid+'-'+i+'" style="'+bks[3]+''+textScale+'height:'+chAry[mid][i]+'px\;white-space:nowrap;"><div onmouseout="event.cancelBubble=true" id="childtext-'+mid+'-'+cid+'-'+i+'" style="'+cllu+'position:relative"><span style="color:'+saLINK+'\;font:'+sfSIZE+' '+sfFONT+'\;font-weight:'+sfWEIGHT+'\;" onclick="if(!cellCLICK){goToUrl(cI['+mid+']['+cid+']['+i+'][0],cI['+mid+']['+cid+']['+i+'][2])}">'+cI[mid][cid][i][1]+'</span></div></div></td>';
		cn+='</tr>';
		}
	cn+='</table></div>';

	//set position
	cLeft = sLeft+slMargin-shSIZE;

	clMargin = 0;
	crMargin = 0;
	if(cP[mid][cid][1]=="left") {
		if(chhOFFSET>0) { clMargin+=chhOFFSET; }
		if(cP[mid][cid][4]>0) { clMargin+=cP[mid][cid][4]; }
		if(chhOFFSET<0) { cLeft+=chhOFFSET; }
		if(cP[mid][cid][4]<0) { cLeft+=cP[mid][cid][4]; }
		cLeft+=sP[mid][0];
		}
	if(cP[mid][cid][1]=="right") {
		mSize=0;
		if(chhOFFSET>0) { crMargin+=chhOFFSET; mSize+=crMargin; }
		if(cP[mid][cid][4]>0) { crMargin+=cP[mid][cid][4]; mSize+=crMargin; }
		if(chhOFFSET<0) { cLeft-=chhOFFSET; }
		if(cP[mid][cid][4]<0) { cLeft-=cP[mid][cid][4]; }
		cLeft-=cP[mid][cid][0]+mSize;
		}

	clMargin+=shSIZE;

	cTop = sTop+stMargin-shSIZE;

	for(i=0;i<cid;i++){
		cTop+=shAry[i]+sbSIZE;
		}
	if(chvOFFSET<0) { cTop+=chvOFFSET; } if(cP[mid][cid][3]<0) { cTop+=cP[mid][cid][3]; }

	ctMargin=sbSIZE;
	if(chvOFFSET>0) { ctMargin+=chvOFFSET; }
	if(cP[mid][cid][3]>0) { ctMargin+=cP[mid][cid][3]; }

	ctMargin+=shSIZE;

	//write submenu
	applyWidth='width:auto;min-width:'+(cP[mid][cid][0]+clMargin)+'px\;white-space:nowrap;';
	if(konqi){applyWidth='width:'+(cP[mid][cid][0]+clMargin)+'px\;';}
	applyWidthII='width:auto;min-width:'+(cP[mid][cid][0]+swPad-sbSIZE)+'px\;white-space:nowrap;';
	if(konqi){applyWidthII='width:'+(cP[mid][cid][0]+swPad-sbSIZE)+'px\;';}
	cNode.parentNode.innerHTML='<div onmouseover="showGrid()" id="childmenu-'+mid+'-'+cid+'" style="visibility:hidden\;position:absolute\;left:'+cLeft+'px\;top:'+cTop+'px\;z-index:'+(zORDER+60)+'\;"><div id="childshadow-'+mid+'-'+cid+'" style="'+shopac+'\;margin-top:'+ctMargin+'px\;margin-left:'+clMargin+'px\;margin-right:'+crMargin+'px\;'+bks[6]+'z-index:'+(zORDER+61)+'\;'+applyWidthII+'height:1px\;">'+cn+'</div></div>';

	//position text layers
	for(i=0;i<cI[mid][cid].length;i++){
		ctObj=document.getElementById('childtext-'+mid+'-'+cid+'-'+i);
		ctt=((ctObj.parentNode.offsetHeight/2)-(ctObj.offsetHeight/2)+svtOFFSET)+"px";
 		ctObj.style.top = ctt;
		if(cP[mid][cid][2]=="left") { ctObj.style.left = stINDENT+"px"; }
		if(cP[mid][cid][2]=="right") { ctObj.style.left = (0-stINDENT)+"px"; }
		}

	//size dropshadow
	cshObj=document.getElementById('childshadow-'+mid+'-'+cid);
	cshObj.style.height=(document.getElementById('childtable-'+mid+'-'+cid).offsetHeight+shPad)+"px";

	//childmenu object
	cnObj = document.getElementById('childmenu-'+mid+'-'+cid);

	//move if remotely triggered and overhanging bottom
	if(remoteTRIGGERING) {
		evcy=parseInt(cnObj.style.top);
		evoh=cnObj.offsetHeight;
		evst=window.pageYOffset;
		if((evcy+evoh)>bHeight) { 
			mctPos=evcy-((evcy+evoh)-bHeight); 
			cnObj.style.top=(mctPos+evst)+"px";
			}
		}
	
	//show childmenu
	cnObj.style.visibility="visible";

	return cnObj;
	}


//clear cell function for sub and child menus
function clearCell(ccObj) {
	if(ui[5]) {
		if(ui[3]) { ccObj.style.backgroundImage = 'url('+bk[3].src+')'; }
		else { ccObj.style.backgroundImage = 'url('+bnk+')'; }
		}
	else {
		if(ui[3]) { ccObj.style.backgroundImage = 'url('+bk[3].src+')'; }
		else { ccObj.style.backgroundColor = bk[3]; }
		}
	ccObj.firstChild.firstChild.style.color = saLINK;
	}


//childmenu cell events
function childCell(mNum,sNum,cNum) {

	clearTimeout(cTimer);
	closeOkay=false;

	if(!keepSubLIT) {
		scObj.firstChild.firstChild.style.color = saLINK;
		if(ui[5]) {
			if(ui[3]) { scObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { scObj.style.backgroundImage = 'url('+bnk+')'; }
			}
		else {
			if(ui[3]) { scObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { scObj.style.backgroundColor = bk[3]; }
			}
		}

	if(previousID[2]>-1) {
		pObj = document.getElementById('childcell-'+previousID[0]+'-'+previousID[1]+'-'+previousID[2]);
		if(ui[5]) {
			if(ui[3]) { pObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { pObj.style.backgroundImage = 'url('+bnk+')'; }
			}
		else {
			if(ui[3]) { pObj.style.backgroundImage = 'url('+bk[3].src+')'; }
			else { pObj.style.backgroundColor = bk[3]; }
			}
		pObj.firstChild.firstChild.style.color = saLINK;
		}
	currentID = [mNum,sNum,cNum];
	previousID = currentID;
	focusID=currentID;

	ccObj = document.getElementById('childcell-'+mNum+'-'+sNum+'-'+cNum);

	if(cI[mNum][sNum][cNum][4]){
		if(ui[5]) {
			ccObj.style.backgroundImage = 'url('+bk[5].src+')';
			}
		else {
			ccObj.style.backgroundImage = 'url('+bnk+')';
			ccObj.style.backgroundColor = bk[5];
			}
		}

	ccObj.firstChild.firstChild.style.color = saHOVER;

	if(altDISPLAY=="status") {
		writeStatus(cI[mNum][sNum][cNum][3]);
		}
	else {
		tInfo=cI[mNum][sNum][cNum][0];
		if(tInfo=="#") { tInfo = ""; }
		writeStatus(tInfo);
		}

	showGrid();
	}



var mn='';
mn+='<div id="master" style="position:absolute\;left:0px\;top:0px\;">';

// event handling grid
var gopac="";
if(redGRID) { gopac="background-color:red"; }

var grw = bWidth;
if(gridWIDTH>0) { grw = gridWIDTH; }
var grh = bHeight;
if(gridHEIGHT>0) { grh = gridHEIGHT; }

mn+='<div id="udm-grid" onmouseover="gridClearMenus()" style="'+gopac+'\;cursor:default\;visibility:hidden\;position:absolute\;top:0px\;left:0px\;z-index:'+(zORDER+10)+'\;width:'+grw+'px\;height:'+grh+'px\;">&nbsp;</div>';


//menu  nodes
mn+='<div id="manch" style="position:absolute\;top:0px\;left:0px\;z-index:'+(zORDER+40)+'\;"></div>';
mn+='<div id="canch" style="position:absolute\;top:0px\;left:0px\;z-index:'+(zORDER+60)+'\;"></div>';


// main navbar
var mbc = bks[1];
var mcbc = bks[0];
var clcu,cllu,mtObj,mcLeft,strCol;
var ofh='overflow:hidden';
if(konqi){ofh='';}

var mnDisplay='';
if(remoteTRIGGERING) { mnDisplay='display:none'; }

if(menuALIGN!="free") {

	//undernav if !free alignment
	strCol=bks[0];
	if(showBORDERS) { strCol=bks[1]; }
	if(stretchMENU||showBORDERS) {
		mn+='<div id="underb" style="'+mnDisplay+'\;cursor:default\;'+strCol+'visibility:visible\;position:absolute\;z-index:'+(zORDER+1)+'\;left:0px\;top:'+absTOP+'px\;width:'+bWidth+'px\;height:'+(navH+(2*bSIZE))+'px\;">';
		if(stretchMENU&&showBORDERS) { mn+='<div style="margin:'+bSIZE+'px\;width:'+(bWidth-(2*bSIZE))+'px\;height:'+navH+'px\;'+bks[0]+'cursor:default">&nbsp;</div>'; }
		mn+='</div>';
		}

	mn+='<div id="udm-navbar" style="'+mnDisplay+'\;'+bks[1]+'position:absolute\;z-index:'+(zORDER+2)+'\;left:'+absLEFT+'px\;top:'+absTOP+'\;width:'+navSpace+'px\;height:'+(navH+(2*bSIZE))+'px\;" class=mTD></div>';
	mcLeft=absLEFT+bSIZE;

	//navbar if !free alignment
	for(i=0;i<mI.length;i++){
		clcu = '';
		if(cellCLICK&&mI[i][0]!=""&&mI[i][0]!="#"&&mI[i][0]!="~") { clcu = ' cursor:'+aCURSOR+'\;'; }
		cllu=' cursor:default\;';
		if(mI[i][0]!=""&&mI[i][0]!="#"&&mI[i][0]!="~") { cllu = ' cursor:'+aCURSOR+'\;'; }
		titleText=""; if(altDISPLAY=="title") { titleText = mI[i][5]; }
		mn+='<div title="'+titleText+'" onfocus="mainCell('+i+')" onmouseover="temSNode=document.getElementById(\'submenu-'+i+'\')\;if(!temSNode){mainCell('+i+')}else{partialMainCell('+i+')}" onmouseout="if(event.clientX<5||event.clientY<5){gridClearMenus()}" onclick="goToUrl(mI['+i+'][0],mI['+i+'][4],['+i+'])" id="maincell-'+i+'" style="'+mnDisplay+'\;z-index:'+(zORDER+3)+'\;visibility:hidden\;position:absolute\;top:'+(absTOP+bSIZE)+'px\;left:'+mcLeft+'px\;'+clcu+mcbc+'width:'+mI[i][2]+'px\;height:'+thisNavH[i]+'px\;'+ofh+'"><table cellpadding=0 cellspacing=0 border=0 width="100%" height="100%" onmouseout="event.cancelBubble=true"><tr><td class=mTD align='+mI[i][3]+'><span onclick="if(!cellCLICK){goToUrl(mI['+i+'][0],mI['+i+'][4])}" id="maintext-'+i+'" style="'+cllu+'position:relative;left:0px;top:0px">'+mI[i][1]+'</span></td></tr></table></div>';
		mcLeft+=bSIZE+mI[i][2];
		}

	}

if(menuALIGN=="free") {

	//navbar if free alignment
	for(i=0;i<mI.length;i++){
		clcu = '';
		if(cellCLICK&&mI[i][0]!=""&&mI[i][0]!="#"&&mI[i][0]!="~") { clcu = ' cursor:'+aCURSOR+'\;'; }
		cllu=' cursor:default\;';
		if(mI[i][0]!=""&&mI[i][0]!="#"&&mI[i][0]!="~") { cllu = ' cursor:'+aCURSOR+'\;'; }
		mn+='<div style="'+bks[1]+'z-index:'+(zORDER+2)+'\;position:absolute\;left:'+(absLEFT+mI[i][7])+'px\;top:'+(absTOP+mI[i][6])+'px\;width:'+(mI[i][2]+(2*bSIZE))+'px\;height:'+(thisNavH[i]+(2*bSIZE))+'px\;"></div>';
		titleText=""; if(altDISPLAY=="title") { titleText = mI[i][5]; }
		mn+='<div title="'+titleText+'" onfocus="mainCell('+i+')" onmouseover="temSNode=document.getElementById(\'submenu-'+i+'\')\;if(!temSNode){mainCell('+i+')}else{partialMainCell('+i+')}" onmouseout="if(event.clientX<5||event.clientY<5){gridClearMenus()}" onclick="if(cellCLICK){goToUrl(mI['+i+'][0],mI['+i+'][4])}" id="maincell-'+i+'" style="'+mnDisplay+'\;z-index:'+(zORDER+3)+'\;position:absolute\;left:'+(absLEFT+mI[i][7]+bSIZE)+'px\;top:'+(absTOP+mI[i][6]+bSIZE)+'px\;visibility:hidden\;'+clcu+mcbc+'width:'+mI[i][2]+'px\;height:'+thisNavH[i]+'px\;'+ofh+'"><table cellpadding=0 cellspacing=0 border=0 width="100%" height="100%" onmouseout="event.cancelBubble=true"><tr><td class=mTD align='+mI[i][3]+'><span onclick="if(!cellCLICK){goToUrl(mI['+i+'][0],mI['+i+'][4])}" id="maintext-'+i+'" style="'+cllu+'position:relative;left:0px;top:0px">'+mI[i][1]+'</span></td></tr></table></div>';
		mcLeft+=bSIZE+mI[i][2];
		}

	}



//write navbar
mn+='</div>';
document.write(mn);



//click to close
function clickToClose() {
	clearSubMenus();
	}
document.onclick = clickToClose;


//load function
var mtt;
function loadFunction() {

	//add event listener for remote triggering
	if(remoteTRIGGERING) { document.addEventListener("mousemove", menuListen, false); }
	
	//position text layers
	for(i=0;i<mI.length;i++){
		mtObj=document.getElementById("maintext-"+i);
		if(typeof mtObj!="undefined"){
			mtt=((thisNavH[i]/2)-(mtObj.offsetHeight/2)+vtOFFSET-(vPADDING/2)-1)+"px";
			if(konqi){mtt=vtOFFSET+"px";}
			mtObj.style.top = mtt;
			if(mI[i][3]=="left") { mtObj.style.left = tINDENT+"px"; }
			if(mI[i][3]=="right") { mtObj.style.left = (0-tINDENT)+"px"; }
			document.getElementById("maincell-"+i).style.visibility="visible";
			}
		}

	//store some objects
	nav = document.getElementById("udm-navbar");
	if(menuALIGN!="free"){nav.style.top=absTOP+"px";}
	grid = document.getElementById("udm-grid");
	sObj = document.getElementById("manch");
	cObj = document.getElementById("canch");

	genericOnloadFunction();
	if(mz7){nsinit();}
	}

window.onload=loadFunction;





// resize / reload trap
function nsinit(){if(allowRESIZE==true){setTimeout("window.onresize=redo", 1000);}}
function redo(){window.location.reload();}
if(!mz7) {if(allowRESIZE==true){window.onresize=new Function("window.location.reload()");}}




//listen for mouse events
var doListen=true;
var mtPos,mtProps,scaroTop,ecX,ecY;
function menuListen(e) {

	if(doListen) { mtPos=[e.clientX+32,e.clientY]; }
	//window.status=mtPos;

	}



//move menu
function activateMenu(mmNum) {
	if(typeof sP[mmNum]=="undefined"||!remoteTRIGGERING) { return false; }
	
	//stop listening
	doListen=false;
	
	//store mouse co-ords
	ecX=mtPos[0];
	ecY=mtPos[1]
	
	//reset offsets
	vOFFSET=0;
	hOFFSET=0;
	sP[mmNum][3]=0;
	sP[mmNum][4]=0;
	
	//remotely create menu
	mainCell(mmNum,false);
	
	//find scroll position
	scaroTop=window.pageYOffset;

	//set child menus alignment
	for(i=0;i<sI[mmNum].length;i++){
		cP[mmNum][i][1]="left";
		}
	
	//convert to useful position
	mtProps=[snObj.offsetWidth,snObj.offsetHeight];
	if(mtPos[0]>(bWidth/2)) { 
		mtPos[0]=ecX-64-mtProps[0]; 
		//set child menus alignment
		for(i=0;i<sI[mmNum].length;i++){
			cP[mmNum][i][1]="right";
			}
		
		}
	if((mtPos[1]+mtProps[1])>bHeight) { 
		mtPos[1]=(ecY)-((mtPos[1]+mtProps[1])-bHeight); 
		}
	hOFFSET=mtPos[0];
	vOFFSET=mtPos[1];
	
	//move menu
	snObj.style.left=hOFFSET+"px";
	snObj.style.top=(vOFFSET+scaroTop)+"px";
	ncObj.style.left=(hOFFSET)+"px";
	ncObj.style.top=((vOFFSET+scaroTop)-thisNavH[mmNum]-bSIZE)+"px";
	sLeft = parseInt(ncObj.style.left);
	if(shType=="string") { sLeft-=(shSIZE*2); }
	sTop = parseInt(ncObj.style.top)+thisNavH[mmNum];
	
	//show menu
	remoteShow(snObj);
	
	//start listening
	doListen=true;
	
	return true;
	}


//show menu
var showTimer;
var showCount=0;
var showPassObj;
function remoteShow(showObj) {
	
	showPassObj=showObj;

	if(showCount==1) {
		clearTimeout(showTimer);
		showCount=0;
		showObj.style.visibility="visible"; 
		}
	else {
		showCount=1;
		showTimer=setTimeout("remoteShow(showPassObj)",40);
		}

	}