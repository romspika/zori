function getURLParameter(sParam) {
	var url = window.location.href;
	var newParam = url.substring(url.lastIndexOf('?')+1);
	if (newParam.length > 20) {
		newParam = '04';
		return newParam;
	} else {
		newParam = newParam.split('=');
		return newParam[1];
	}
}

function shownews(kod) {

if (kod == '04') { newnews = news; }
if (kod == '03') { newnews = news03; }
if (kod == '02') { newnews = news02; }
if (kod == '01') { newnews = news01; }	
	
//var destination = offset().top ;
//$("html").animate({ scrollTop: destination}, 1000);	
	
for (i = 0; i < newnews.length; i++) {

str = newnews[i][3];
str = str.slice(str.lastIndexOf('#')+1);
var fulllink = 'https://www.kasimovskie-zori.ru/news.html#' + str;

document.write('<div class="blog_post">');
document.write('<div class="row">');

document.write('<div class="col-xl-7 col-lg-6">');
document.write('<div class="blog_post_image"><img src="'+newnews[i][1]+'" alt="" width="700px"></div>');
document.write('</div>');

document.write('<div class="col-xl-5 col-lg-6">');
document.write('<div class="blog_post_content">');
document.write('<div class="bp_date trans_200" ><a href="javascript://">'+newnews[i][4]+'</a></div>');

document.write('<div class="pb_title" style="line-height: 22px;"><a href="'+fulllink+'">'+newnews[i][2]+'</a></div>');

document.write('<div class="pb_text" >');
document.write('<p style="line-height: 22px;">'+newnews[i][5]+'</p>');
document.write('</div>');
document.write('<div class="button blog_button"><a href="javascript://" onclick="$(\'#'+str+'\').slideToggle(\'slow\');">Читать дальше</a></div>');
document.write('</div>');
document.write('</div>');
/*****/

document.write('  <div class="textblock articles" id="'+str+'" style="text-align:center; width:100%; border-bottom: #aaaaaa solid 3px;margin-bottom:20px; padding:20px;float:left;">');
document.write(' <a name="'+str+'"></a>');
document.write(' <br /><br />');
document.write(' <p align="right"><font color="#999999" size="+1">'+newnews[i][4]+'</font>&nbsp;&nbsp;</p>');
document.write(' <font color="#555555" size="+3">'+newnews[i][5]+'</font><font size="+1"><br /><br />');

document.write('<div style="width:100%; margin-bottom:20px; border:#0f0 solid 0px; float:left;">');
document.write('<div style="width:47%; min-width:370px; float:left; text-align:left;">'+newnews[i][6]+'</div>');
document.write('<div style="width:5%; float:left; text-align:left;">&nbsp;</div>');
document.write('<div style="width:47%; min-width:370px; float:left; text-align:left;">'+newnews[i][7]+'</div>');
document.write('</div>');

document.write('<div style="width:100%; margin-top:20px; border:#f00 solid 0px;float:left;">');
for (j = 0; j < 20; j++) {
   if (newnews[i][8][j].length > 0) {
      document.write(' <a href="'+newnews[i][8][j]+'" target="_blank"><img src="'+newnews[i][8][j]+'" width="25%" style="margin:4px;" /></a>');  
    }
}
document.write('</div>');

document.write('</div>');



/*****/

document.write('</div>');
document.write('</div>');

}

}