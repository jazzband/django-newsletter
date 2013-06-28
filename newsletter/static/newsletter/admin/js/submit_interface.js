var SubmitInterface = {
    changed: false,

    init: function(submitname) {
        var submitlink = django.jQuery(submitname);
        submitlink.click(function() {
            SubmitInterface.process();
        });
        submitlink.attr('href', '#');
        django.jQuery('form:first :input').change(function() {
            SubmitInterface.changed = true;
        });
    },

    process: function() {
        if (SubmitInterface.changed) {
            var result = confirm(gettext('The submission has been changed. It has to be saved before you can submit. Click OK to proceed with saving, click cancel to continue editing.'));
            if (result) {
                django.jQuery('form:first [name="_continue"]').click();
            }
        } else {
            window.location = 'submit/';
        }
    }
};
