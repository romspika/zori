function setActiveMenu(punktmenu) {

   obj = document.getElementById('menu1');
   if (punktmenu == 'menu1') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }
	
   obj = document.getElementById('menu2');
   if (punktmenu == 'menu2') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }

   obj = document.getElementById('menu3');
   if (punktmenu == 'menu3') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }

   obj = document.getElementById('menu4');
   if (punktmenu == 'menu4') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }

   obj = document.getElementById('menu5');
   if (punktmenu == 'menu5') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }

   obj = document.getElementById('menu6');
   if (punktmenu == 'menu6') { obj.classList.add('active');  } 
	else { obj.classList.remove('active'); }
}