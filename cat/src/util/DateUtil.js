// yyyy-MM-dd hh:mm:ss
Date.prototype.format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1,                 //月份 
        "d+": this.getDate(),                    //日 
        "h+": this.getHours(),                   //小时 
        "m+": this.getMinutes(),                 //分 
        "s+": this.getSeconds(),                 //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds()             //毫秒 
    };
    if (/(y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }
    for (var k in o) {
        if (new RegExp("(" + k + ")").test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        }
    }
    return fmt;
}


const DateUtil = {
    // 实际长度为 length+1
    lastNMinuteStrs: (length) => {
        let results = []

        let temp = new Date();

        results.push(temp.format('hh:mm'))
        for (let i = 0; i < length; i++) {
            let min = temp.getMinutes()  //获取当前分钟数(0-59)
            temp.setMinutes(min - 1)

            results.push(temp.format('hh:mm'))
        }

        return results.reverse()
    },
}

export {
    DateUtil
};

