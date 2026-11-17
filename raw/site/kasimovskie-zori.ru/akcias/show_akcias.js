// Модуль использует disableScroll(); и enableScroll(); для блокирования скроллинга.
// Функции расположены в файле  js/disableScroll.js

function place_slider_akcias() {
document.write('     <div id="slider_akcias" class="slider_akcias">');
document.write('		<div class="akcias_header" style="">');
document.write('		     <span id="x_button_akcias" class="button-exit-akcias" style="float:right; margin-right: 12px;" onclick="hide_akcias();">+</span>');
document.write('		</div>');

document.write('		<div id="akcias-headline" class="akcias-header akcias-headline" style="">Yfpdfybt frebb</div>');
document.write('		<div class="akcias-header"><img src="+ akcias[0][1]+" id="akcias-img"></div>');
		
document.write('		<div id="akcias-allcontent" class="akcias-allcontent">');
document.write('			<span id="akcias-content">32432 123 254 5 135 456 56 456 456 46435 6456 43756 7567 5467 567456 75467 4567 575 6756 757 546 74567 4567 1235 31245 3145 3456 21356</span>');
document.write('		</div>');

document.write('	 </div>');
}

function show_akcias(num) {
        //var widthBefore = document.body.offsetWidth;

	document.getElementById('akcias-headline').innerHTML = akcias[num][0]; 
	document.getElementById('akcias-img').src = akcias[num][1]; 
	document.getElementById('akcias-content').innerHTML = akcias[num][2]; 
        
	document.getElementById('slider_akcias').setAttribute('style','transform: translateX(-400px)'); 

	//document.body.style.overflow = "hidden";
	//document.body.setAttribute('style','overflow: hidden');
	
        //var widthNow = (document.body.offsetWidth-widthBefore).toString();
        //document.body.setAttribute('style','margin-right: '+ widthNow + 'px');

       disableScroll();

}

function hide_akcias() {
	document.getElementById('slider_akcias').setAttribute('style','transform: translateX(400px)');  
	//document.body.style.overflow = "";
        //document.body.setAttribute('style','margin-right: 0px');
	
	enableScroll();
      
}


function showakcias() {

document.write('<div class="oneakcias">');
document.write('	<div class="akciaspic">');
document.write('		<img src="' + akcias[i][0]  +'"/>');
document.write('	</div>');
document.write('	<div class="akciasname">');
document.write('		<span>' + akcias[i][1] + '</span>');
document.write('	</div>');	
document.write('	<div class="akciascontent">');
document.write('		<span>' + akcias[i][4] + '</span>');
document.write('		<hr class="fade" width="90%" />');
document.write('	</div>');	
document.write('</div>');
}

