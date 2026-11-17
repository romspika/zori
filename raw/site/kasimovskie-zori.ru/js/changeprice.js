var jek = 0;	
var stnd = 1;
var stnd2 = 1;
var stnd2Oka = 0;
var stnd3 = 0;
var half = 0;
var lux = 0;


var priceperiods = [
    'Май<br/>Июнь<br/>2026', '<br/>Июль<br/>2026', '<br/>Август<br/>2026', 
    '<br/>Сентябрь<br/>2026', '<br/>Октябрь<br/>2026', '<br/>Ноябрь<br/>2026', '<br/>Декабрь<br/>2026' 
];

// С ЗАВТРАКОМ И УЖИНОМ (ПРПОГРАММА «ЛАЙТ»)

var priceInperiod = [
//СТАНДАРТ одноместный
// 0 - Одноместное размещение 
    ['3900', '3900', '3900', '3400', '3400', '2900', '2900'],
    
//СТАНДАРТ 2-местный однокомнатный
// 1 - Одноместное размещение
    ['5400', '5400', '5400', '4800', '4800', '4100', '4100'],	
// 2 - Двухместное размещение
    ['7800', '7800', '7800', '6800', '6800', '5800', '5800'],	
// 3 - Осн. место для ребенка (3-14 лет)
    ['2500', '2500', '2500', '2500', '2500', '2500', '2500'],	
// 4 - Доп. место (3-14 лет)
    ['2300', '2300', '2300', '2300', '2300', '2300', '2300'],

//СТАНДАРТ 2-местный однокомнатный (с видом на Оку)
// 5 - Одноместное размещение
    ['5600', '5600', '5600', '4950', '4950', '4300', '4300'],
// 6 - Двухместное размещение
    ['8200', '8200', '8200', '7200', '7200', '6200', '6200'],
// 7 - Осн. место для ребенка (3-14 лет)
    ['2500', '2500', '2500', '2500', '2500', '2500', '2500'],	
// 8 - Доп. место (3-14 лет)
    ['2300', '2300', '2300', '2300', '2300', '2300', '2300'],

//СТАНДАРТ 3-местный однокомнатный
// 9 - Двухместное размещение
    ['8600', '8600', '8600', '7600', '7600', '6500', '6500'],
// 10 - Трёхместное размещение
    ['11700', '11700', '11700', '10200', '10200', '8700', '8700'],
// 11 - Осн. место для ребенка (3-14 лет)
    ['2500', '2500', '2500', '2500', '2500', '2500', '2500'],	
// 12 - Доп. место (3-14 лет)
    ['2300', '2300', '2300', '2300', '2300', '2300', '2300'],

//ПОЛУЛЮКС однокомнатный
// 13 - Одноместное размещение
    ['6100', '6100', '6100', '5400', '5400', '4700', '4700'],
// 14 - Двухместное размещение
    ['8800', '8800', '8800', '7700', '7700', '6600', '6600'],
// 15 - Доп. место (3-14 лет)
    ['2300', '2300', '2300', '2300', '2300', '2300', '2300'],    

//ЛЮКС однокомнатный
// 16 - Одноместное размещение
    ['6500', '6500', '6500', '5800', '5800', '5000', '5000'],  
// 17 - Двухместное размещение
    ['9300', '9300', '9300', '8150', '8150', '7000', '7000'],  
// 18 - Доп. место (3-14 лет)
    ['2300', '2300', '2300', '2300', '2300', '2300', '2300'] 
];




var priceperiodsEat = [
    '', '', '<br/>Май<br/>2026', '<br/>Июнь<br/>2026', 'Июль<br/>Август<br/>2026', 
    'Сентябрь<br/>Октябрь<br/>2026', 'Ноябрь<br/>Декабрь<br/>2026'];

// ПРОЖИВАНИЕ С ЗАВТРАКОМ

var priceInperiodEat = [
//СТАНДАРТ одноместный
// 0 - Одноместное размещение 
    ['-', '-', '3200', '3700', '3900', '3400', '2900'],
    
//СТАНДАРТ 2-местный однокомнатный
// 1 - Одноместное размещение
    ['-', '-', '4500', '5200', '5400', '4800', '410'],	
// 2 - Двухместное размещение
    ['-', '-', '6400', '7400', '7800', '6800', '5800'],	
// 3 - Осн. место для ребенка (3-14 лет)
    ['-', '-', '2500', '2500', '2500', '2500', '2500'],	
// 4 - Доп. место (3-14 лет)
    ['-', '-', '2300', '2300', '2300', '2300', '2300'],

//СТАНДАРТ 2-местный однокомнатный (с видом на Оку)
// 5 - Одноместное размещение
    ['-', '-', '4700', '5400', '5600', '4950', '4300'],
// 6 - Двухместное размещение
    ['-', '-', '6750', '7800', '8200', '7200', '6200'],
// 7 - Осн. место для ребенка (3-14 лет)
    ['-', '-', '2500', '2500', '2500', '2500', '2500'],	
// 8 - Доп. место (3-14 лет)
    ['-', '-', '2300', '2300', '2300', '2300', '2300'],

//СТАНДАРТ 3-местный однокомнатный
// 9 - Двухместное размещение
    ['-', '-', '7100', '8200', '8600', '7600', '6500'],
// 10 - Трёхместное размещение
    ['-', '-', '9600', '11100', '11700', '10200', '8700'],
// 11 - Осн. место для ребенка (3-14 лет)
    ['-', '-', '2500', '2500', '2500', '2500', '2500'],	
// 12 - Доп. место (3-14 лет)
    ['-', '-', '2300', '2300', '2300', '2300', '2300'],

//ПОЛУЛЮКС однокомнатный
// 13 - Одноместное размещение
    ['-', '-', '5100', '5900', '6100', '5400', '4700'],
// 14 - Двухместное размещение
    ['-', '-', '7300', '8400', '8800', '7700', '6600'],
// 15 - Доп. место (3-14 лет)
    ['-', '-', '2300', '2300', '2300', '2300', '2300'],

//ЛЮКС однокомнатный
// 16 - Одноместное размещение
    ['-', '-', '5400', '6200', '6500', '5800', '5000'],  
// 17 - Двухместное размещение
    ['-', '-', '7700', '8900', '9300', '8150', '7000'],  
// 18 - Доп. место (3-14 лет)
    ['-', '-', '2300', '2300', '2300', '2300', '2300'],
];



function changeprice_withfader(k) {
	
	jek = jek + k;
	if (jek < 6) {
		document.getElementById('button-right').style.backgroundColor = '#FFF'; 
	}
	if (jek == 6) {
		document.getElementById('button-right').style.backgroundColor = '#999'; 
	}
	if (jek > 6) {
		jek = 6;
		return;
	}

	if (jek > 0) {
		document.getElementById('button-left').style.backgroundColor = '#FFF'; 
	}
	if (jek == 0) {
		document.getElementById('button-left').style.backgroundColor = '#999'; 
	}
	if (jek < 0) {
		jek = 0;
		return;
	}
	
	
	for (var i = 0; i < 19; i++) {
		$('#pricefader'+i.toString()).animate({ opacity: 'toggle' }, 200	);        
	}	
   		
   		
	
   	$('#pricefader0').text(priceperiods[jek]);
   
   	for (var i = 0; i < 18; i++) {
   		$('#pricefader'+(i+1).toString()).text(priceInperiod[i][jek]);
   	}



	for (var i = 0; i < 19; i++) {
		$('#pricefader'+i.toString()).animate({ opacity: 'toggle' }, 200	);        
	}

	
}

function opentr(idname) {
	   $('#'+idname).slideToggle('slow'); 
	
	   if (idname == 'stnd') { 
		    stnd = 1 - stnd;	
		    if (stnd == 0) {	document.getElementById('imgstnd').src = 'images/plus.png'; }
		    if (stnd == 1) {	document.getElementById('imgstnd').src = 'images/minus.png'; }
	   }
	   if (idname == 'stnd2') { 
		    stnd2 = 1 - stnd2;	
		    if (stnd2 == 0) {	document.getElementById('imgstnd2').src = 'images/plus.png'; }
		    if (stnd2 == 1) {	document.getElementById('imgstnd2').src = 'images/minus.png'; }
	   }		
	   if (idname == 'stnd2Oka') { 
		    stnd2Oka = 1 - stnd2Oka;	
		    if (stnd2Oka == 0) {	document.getElementById('imgstnd2Oka').src = 'images/plus.png'; }
		    if (stnd2Oka == 1) {	document.getElementById('imgstnd2Oka').src = 'images/minus.png'; }
	   }	
	   if (idname == 'stnd3') { 
		    stnd3 = 1 - stnd3;	
		    if (stnd3 == 0) {	document.getElementById('imgstnd3').src = 'images/plus.png'; }
		    if (stnd3 == 1) {	document.getElementById('imgstnd3').src = 'images/minus.png'; }
	   }	
	   if (idname == 'half') { 
		    half = 1 - half;	
		    if (half == 0) {	document.getElementById('imghalf').src = 'images/plus.png'; }
		    if (half == 1) {	document.getElementById('imghalf').src = 'images/minus.png'; }
	   }
	   if (idname == 'lux') { 
		    lux = 1 - lux;	
		    if (lux == 0) {	document.getElementById('imglux').src = 'images/plus.png'; }
		    if (lux == 1) {	document.getElementById('imglux').src = 'images/minus.png'; }
	   }
}

function show_period(i)
{
   document.write(priceperiods[i]);
}

function show_periodEat(i)
{
   document.write(priceperiodsEat[i]);
}

function show_priceInperiod(i, j)
{
   document.write(priceInperiod[i][j]);
}

function show_priceInperiodEat(i, j)
{
   document.write(priceInperiodEat[i][j]);
}

function witheat(eat) {
	//alert('iseat=',iseat, ' eat=' , eat);
	//if (iseat == eat) { return; }
	
	for (var i = 0; i < 19; i++) {
			for (var j = 0; j < 7; j++) {
				a = String(i);
				// alert(a);
				if (a.length == 1) { a = '0' + a; }
				a = 's' + a + 'e0' + String(j);
				$('#' + a).animate({ opacity: 'toggle' }, 200	);    				
				if (eat == 0) {
					$('#'+ a).text(priceInperiodEat[i][j]);
					// document.getElementById('button0').style.backgroundColor = '#36C'; 					
					// document.getElementById('button1').style.backgroundColor = '#CBCBCB'; 									//document.getElementById('button2').style.backgroundColor = '#CBCBCB'; 					
				} else {
					$('#'+ a).text(priceInperiodEat[i][j]);
					// document.getElementById('button0').style.backgroundColor = '#CBCBCB'; 				
					// document.getElementById('button1').style.backgroundColor = '#36C';					
					// document.getElementById('button2').style.backgroundColor = '#36C';					
				}
				$('#' + a).animate({ opacity: 'toggle' }, 200	);    
			}
			// await new Promise(resolve => setTimeout(resolve, 100)); 
		}
	
}