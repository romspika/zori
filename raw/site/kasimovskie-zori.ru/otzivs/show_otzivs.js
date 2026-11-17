function place_vidget_otziv() {
document.write('<div id="vidget_otziv" class="vidget_otziv" onmouseenter=\'vidget_wide(300);\' onmouseleave=\'vidget_wide(250);\'  >');
document.write('   <div style="text-align:left; margin-left:10px;color:#333;">');
document.write('       <font size="-1">Œ“«€¬€ Õ¿ÿ»’ √Œ—“≈…</font>');
document.write('   </div>');
document.write('   <div style="text-align:left; margin-left:10px;"  >');
document.write('       <img src="otzivs/images/photo-vidget.jpg" id="photo-vidget" onclick=\'show_otziv();\'> ');
document.write('   </div>');
document.write('</div>');
}	

function place_slider_otziv() {
document.write('     <div id="slider" class="slider slider_hidden">');
document.write('		<div class="otziv-header" style=""><span id="x_button" class="button-exit" style="float:right; margin-right: 12px;" onclick="hide_otziv();">+</span></div>');
document.write('		<div class="otziv-headder otziv-rating" style="margin-left:20px;">4.9</div>');
document.write('		<div class="otziv-headder otziv-stars"><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /></div>');
document.write('		<div class="otziv-headder otziv-quan">(653 ÓÚÁ˚‚‡)</div>');
		
document.write('		<div class="otziv-allcontent">');
		
document.write('			<script>showotzivs();<\/script>');
/*document.write('			<script>showotzivs();<\/script>');*/
			
document.write('		</div> <!-- ALL CONTENT-->');
document.write('	 </div>');

}

function vidget_wide(w) {
  s = "width:" + String(w) + "px";
  document.getElementById('vidget_otziv').setAttribute("style",s);
  if (w == 250) {
	  document.getElementById('photo-vidget').src = 'otzivs/images/photo-vidget.jpg';
  } else {
	  document.getElementById('photo-vidget').src = 'otzivs/images/photo-vidget2.jpg';
  }
  return;
}

var scrtop;

function show_otziv() {
	document.getElementById('slider').setAttribute('style','transform: translateX(-400px)'); 

	document.body.style.overflow = "hidden";

//      var widthNow = document.body.offsetWidth;
//        document.body.setAttribute('style','margin-right: '+ (widthNow - widthBefore).string + 'px');	


}

function hide_otziv() {
	document.getElementById('slider').setAttribute('style','transform: translateX(400px)');  
	
  	  document.body.style.overflow = "";
//        document.body.setAttribute('style','margin-right: 0px');


}



function showotzivs() {

for (i = 0; i < otziv.length; i++) {
document.write('<div class="oneotziv">');
document.write('	<div class="otzivpic">');
document.write('		<img src="' + otziv[i][0]  +'"/>');
document.write('	</div>');
document.write('	<div class="otzivname">');
document.write('		<span>' + otziv[i][1] + '</span>');
document.write(	    '<div style="margin-top: 10px; border: #000 solid 0px;">');
document.write('		    <div style="width: 100px; float:left;">');

if (otziv[i][2] == 4) { document.write('				<img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star-0.jpg" />'); }
if (otziv[i][2] == 5) { document.write('				<img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" /><img src="otzivs/images/star.jpg" />'); }

document.write('			</div>');
document.write('		    <div style="width: 110px; float:left; margin-bottom:5px;">');
document.write('				<span class="otzivdate" style="margin-top:2px;">' + otziv[i][3] + '</span>');
document.write('			</div>');	
document.write('		</div>');
document.write('	</div>');
document.write('	<div class="otzivcontent">');
document.write('		<span>' + otziv[i][4] + '</span>');
document.write('		<!--hr class="fade" width="90%" /-->');
document.write('		<table class="tblline" width="90%" border="0" />');
document.write('			<tr><td></td></tr>');
document.write('		</table>');
document.write('	</div>')	
document.write('</div>');
	}
}