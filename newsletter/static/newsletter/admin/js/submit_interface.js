var SubmitInterface = {
    changed: false,

    init: function(submitname) {
        var submitlink = django.jQuery(submitname);
        var initial_href = submitlink.attr('href');
        submitlink.click(function() {
            SubmitInterface.process(initial_href);
        });
        submitlink.attr('href', '#');
        django.jQuery('form:first :input').change(function() {
            SubmitInterface.changed = true;
        });
    },

    process: function(href) {
        if (SubmitInterface.changed) {
            var result = confirm(gettext('The submission has been changed. It has to be saved before you can submit. Click OK to proceed with saving, click cancel to continue editing.'));
            if (result) {
                django.jQuery('form:first [name="_continue"]').click();
            }
        } else {
            window.location = href;
        }
    }
};
