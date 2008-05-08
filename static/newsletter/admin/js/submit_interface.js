var SubmitInterface = {
    changed: false,
    
    init: function(submitname) {
        submitlink = document.getElementById(submitname);
        submitlink.href = 'javascript:SubmitInterface.process()';
        addEvent(document.forms[0], "change", function(e) { SubmitInterface.changed = true; });
    },
    
    process: function() {
        if (SubmitInterface.changed) {
            result = confirm(gettext('The submission has been changed. It has to be saved before you can submit. Click OK to proceed with saving, click cancel to continue editing.'));
            if (result) {
                document.forms[0]._continue.click();
            }
        } else {
            window.location = 'submit/';
        }
    }
};
