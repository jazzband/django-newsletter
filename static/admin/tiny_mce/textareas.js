tinyMCE.init({
	mode : "textareas",
	theme : "advanced",
	plugins : "fullscreen",
	
	theme_advanced_buttons1 : "fullscreen,|,undo,redo,|,formatselect,|,italic,|,charmap,|,bullist,numlist,|,link,unlink,|,cleanup,code,",
	theme_advanced_buttons2 : "",
	theme_advanced_buttons3 : "",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_blockformats: "h3,p",
	theme_advanced_path_location : "bottom",

	theme_advanced_resizing : true,
	force_p_newlines : true,
	paste_auto_cleanup_on_paste : true,
	verify_html : true,

	browsers : "msie,gecko,opera",
	entity_encoding : "raw"
	
});


