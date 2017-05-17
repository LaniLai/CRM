/**
 * Created by lenovo on 2017/4/26.
 */

$(document).ready(function () {
    bindDbClick();
    bindSubmit();
    bindChooseallOrClearall();
    bindChooseallFilter();
});

function bindDbClick() {
    $('div.selector').on('dblclick', 'option', function () {
        var option = document.createElement('option');
        $(option).attr('value',$(this).val());
        $(option).text($(this).text());
        var destination = $(this).parent().parent().siblings().find('select');
        $(destination).append(option);
        $(this).remove()
    })
}
function bindSubmit() {
    $('#save').click(function () {
        $('div.selector .select-right select[name]').find('option').attr('selected', true)
    })
}

function bindChooseallOrClearall() {
    $('.selector a.active').click(function () {
        var options = $(this).prev().find('option');
        $(this).parent().siblings().find('select').append(options);
    })
}

function bindChooseallFilter() {
    $('#filter').bind('input onpropertychange', function () {
        var selectId = $(this).parent().next().attr('id');
        var filterText = $(this).val().toLowerCase();
        $('#'+selectId).children().each(function () {
            if($(this).text().toLowerCase().search(filterText) != -1){
                $(this).show();
            }else {
                $(this).hide();
            }
        })
    })
}