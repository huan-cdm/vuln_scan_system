//fofa搜索语法
function myFunction() {
  alert("从标题中搜索北京:  title=\"beijing\"\n从http头中搜索elastic:  header=\"elastic\"\n从html正文中搜索网络空间测绘:  body=\"网络空间测绘\"\n搜索根域名带有qq.com的网站:  domain=\"qq.com\"\n查询IP为220.181.111.1的C网段资产:  ip=\"220.181.111.1/24\"\n查找相同的网站指纹:  fid=\"sSXXGNUO2FefBTcCLIT/2Q==\"\n查找备案号为京ICP证030173号的网站:  icp=\"京ICP证030173号\"\n查找网站正文中包含js/jquery.js的资产:  js_name=\"js/jquery.js\"\n查找js源码与之匹配的资产:  js_md5=\"82ac3f14327a8b7ba49baa208d4eaa15\"\n查找cname为ap21.inst.siteforce.com的网站:  cname=\"ap21.inst.siteforce.com\"\n查找cname包含siteforce.com的网站:  cname_domain=\"siteforce.com\"\n从url中搜索.gov.cn:  host=\".gov.cn\"\n查找对应6379端口的资产:  port=\"6379\"\n查询服务器状态为402的资产:  status_code=\"402\"\n搜索指定国家(编码)的资产:  country=\"CN\"\n搜索指定行政区的资产:  region=\"Xinjiang\"\n搜索指定城市的资产:  city=\"Ürümqi\"\n搜索证书(https或者imaps等)中带有baidu的资产:  cert=\"baidu\"");
}


  //访问网址
      function visitthewebsite(value) {
        var regex =  /^(\w+):\/\/([^:/]+)(:\d+)?/;
        var match = value.match(regex); 
        //alert(match[0])
           window.open(""+match[0]+"");
        }



  //ajax异步启动fofa批量扫描接口
      function startfofabatchfunc() {
        $.ajax({
              url: '/startbatchfofainterface/',
              method: 'GET',
              success: function (res) { 
                  console.log(res)
                  console.log('fofa批量扫描接口已启动成功')
              },
              error: function () {
                  alert('fofa批量扫描接口已启动出错')
              },
              complete: function () {
                  alert('fofa批量扫描接口已启动完成')
              }
          })
        }
     


  //ajax异步停止扫描
      function killfofabatchfunc() {
        $.ajax({
              url: '/killbatchfofainterface/',
              method: 'GET',
              success: function (res) { 
                  console.log(res)
                  console.log('fofa批量扫描接口已停止')
              },
              error: function () {
                  alert('ffofa批量扫描接口内部出现错误')
              },
              complete: function () {
                  alert('fofa批量扫描接口已停止')
              }
          })
        }
     


//nuclei扫描结果预览
function fofapreviewfunc(value) {
    window.open("/fofasearchpreview/");
}
