function meduslugishow(medusluga) {

document.writeln('<p align="center" style="margin-top:20px; margin-bottom:20px; width:100%;"><font size="+1" color="#ffffff"><strong>'+meduslugidate+'</strong></font><br /></p>');

document.writeln(' <font size="+1">');   
document.writeln('<table class="stripetable" width="100%" cellpadding="4px" cellspacing="2px" border="1">');
document.writeln('<tr height="30px">');
document.writeln('  <th bgcolor="#2e3f61" width="8%"><font size="+1">N</font></th>');
document.writeln('  <th bgcolor="#2e3f61" width="72%"><font size="+1">Наименование медицинской услуги</font></th>');   
document.writeln('  <th bgcolor="#2e3f61" width="20%"><font size="+1">Цена, руб</font></th>');   
document.writeln('</tr>');

/*if (medusluga != 0) {
document.writeln('<tr style="background:#0FC;">');
document.writeln('	<td colspan="3" style="text-align:center; background-color:#F93;"><font size="0"><strong>УСЛУГИ,<br />ВКЛЮЧАЕМЫЕ В ЛЕЧЕБНУЮ ПРОГРАММУ</strong></strong></td>');
document.writeln('</tr>');    
}*/


for (i = 0; i < meduslugi.length; i++) { 

if ((medusluga == 0)||meduslugi[i][0] == medusluga) {

if (meduslugi[i][1] == '0') {
document.writeln('	 <tr style="background:#0FC;">');
document.writeln(' 	 <td colspan="3" style="text-align:center; background-color:#6C9;"><strong>'+meduslugi[i][2]+'</strong></td>');
document.writeln('   </tr> ');
} else {
document.writeln('<tr style="height:30px;">');
document.writeln('	<td>'+meduslugi[i][1]+'</td><td>'+meduslugi[i][2]+'</td><td align="right">'+meduslugi[i][3]+'</td>');
document.writeln('</tr>'); 	
}
};

}

document.writeln('<tr>'); 	
document.writeln('  <th colspan="3">&nbsp;</th>'); 	
document.writeln('</tr>'); 	
document.writeln('</table>'); 	

}