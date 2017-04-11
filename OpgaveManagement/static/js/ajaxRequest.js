(function (global) {

    sentData = function(data,request_code, method) {
		return  new loadData( data,request_code, method );
	};
	 loadData = function(data,request_code, method) {
	     var promise = new Promise();
        request_code = '/' + request_code + '/';
        $.ajax({
            url: request_code,
            type: method,
            dataType: "json",
            data: JSON.stringify(data)// 转换为json类型
        }).done(function (reponse_data) {
            try {
                if(reponse_data.status == 0){
                  promise.resolve(reponse_data);
                }else {
                    promise.reject(reponse_data);
                }
            }
            catch(e){
                console.log(e);
            }

        }).fail(function (error) {
            var context = {status:error.status, content:""};
            switch (error.status) {
                case 400: {
                    // 错误的请求
                    context.content = "错误的请求";
                }
                    break;
                case 403: {
                    // 需要验证token
                    context.content = "需要验证token";
                }
                    break;

                case 404: {
                    // 资源不存在
                    context.content = "url错误";
                }
                    break;

                case 408: {
                    // 超时
                    context.content = "超时";
                }
                    break;

                case 500: {
                    //服务器的问题
                    context.content = "服务器出现问题";
                }
                    break;

                default: {
                    // 其他问题
                }
                    break;
            }
            try {
               promise.reject(context);
            }
            catch(e){
                console.log(e);
            }

        });
        return promise;
    };


var Promise = function () {
    this.callbacks = [];
};

Promise.prototype = {
    construct:Promise,
    resolve:function(result){
        this.complete("resolve", result)
    },
    reject:function(result){
        this.complete("reject", result)
    },
    complete:function(type, result){

        while (this.callbacks[0]){
          try {
         var method = this.callbacks.pop()[type];
        }
        catch (e){
            console.log(e);
        }
        if (method){
               method(result);
               break;
        }
        }
    },
    success: function (method) {
        this.callbacks.push({
            resolve:method,
            reject:undefined
        });
        return this;
    },
    fail:function (method) {
           this.callbacks.push({
               resolve:undefined,
               reject:method
        });
        return this;
    }
};
if (!global){
    window.sentData= sentData;
}
return sentData;
})();













