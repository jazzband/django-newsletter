tinyMCE.init({
	mode : "textareas",
	theme : "advanced",
	plugins : "fullscreen,paste",
	
	theme_advanced_buttons1 : "fullscreen,|,undo,redo,|,formatselect,|,italic,|,charmap,|,bullist,numlist,|,link,unlink,|,pastetext, pasteword,cleanup,code,",
	theme_advanced_buttons2 : "",
	theme_advanced_buttons3 : "",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_blockformats: "h3,p",
	theme_advanced_path_location : "bottom",

	paste_create_paragraphs : true,
	paste_create_linebreaks : true,
	paste_use_dialog : true,
	paste_auto_cleanup_on_paste : true,

	theme_advanced_resizing : true,
	force_p_newlines : true,
	
	apply_source_formatting : true,

	verify_html : true,

	browsers : "msie,gecko,opera",
	entity_encoding : "raw",

    width : "450",
    height : "350"
	
});


