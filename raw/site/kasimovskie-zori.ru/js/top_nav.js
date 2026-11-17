//var h_hght = 1330; // высота шапки
var h_mrg = 80;    // отступ когда шапка уже не видна
$(function(){
 $(window).scroll(function(){
    var top = $(this).scrollTop();
    var elem = $('#top_nav');
	
	 var position = $("#endOfTable").offset();
//alert(position.top);	 
//	document.getElementById('pricefader4').innerHTML = String(position.top);  	
	//var position = document.getElementById('podstava').getBoundingClientRect();
	 	 
   
	if (top+h_mrg < h_hght) {
     	elem.css('top', (h_hght-top));
		
    } else {
     	elem.css('top', h_mrg);
    }
	if (top > position.top) {
		elem.css('top', (h_hght-top));
	} 
  });
});


var h_hght2 = 920;
var h_mrg2 = 80;    // отступ когда шапка уже не видна
$(function(){
 $(window).scroll(function(){

	 
    var top = $(this).scrollTop();
    var elem = $('#top_nav2');
    var elembaze = $('#podstava2').offset().top;	 
	
	 var position = $("#endOfTable").offset();

    if (top+h_mrg2 < elembaze) {
     elem.css('top', (elembaze-top));
    } else {
     elem.css('top', h_mrg2);
    }
  });
});
