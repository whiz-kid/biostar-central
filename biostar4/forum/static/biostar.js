
$(document).ready(function () {
    var wmd = $('#wmd-input')
    if (wmd.length) {
        var converter = new Markdown.Converter();
        var editor = new Markdown.Editor(converter);
        editor.run();
    }
});