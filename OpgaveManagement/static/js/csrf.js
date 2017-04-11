/**
 * Created by malizhi on 2017/3/25.
 */
// 解决ajax post提交返回返回403的问题
function setCsrftoken() {
    var csrftoken = $.cookie('csrftoken');
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
