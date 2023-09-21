//删除修改功能提示
function myFunction() {
  alert("删除功能未开启,请联系管理员!!!");
}
function myFunction1() {
  alert("修改功能未开启,请联系管理员!!!");
}

//ajax异步删除数据
function deletefunc(value) {

  $.ajax({
    url: '/deletebyid?id=' + value,
    method: 'GET',
    success: function (res) {
      console.log(res)
      console.log('删除成功')
    },
    error: function () {
      alert('删除出错')
    },
    complete: function () {
      alert('删除完成')
    }
  })

}

//ajax异步添加数据
function addvulnfunc() {
  var vulnname = $('input[name="vulnname"]').val();
  var ip = $('input[name="ip"]').val();
  //录入数据时，将input框中的数据分别利用js添加到异步查询1和异步查询3的文本框中。
  var ip_key = document.getElementById("input3");
  var vulnname_key = document.getElementById("input4");
  ip_key.value = ip;
  vulnname_key.value = vulnname;
  $.ajax({
    url: '/adddata/',
    method: 'POST',
    data: {
      vulnname: vulnname,
      ip: ip
    },
    success: function (res) {
      console.log(res)
      //console.log(vulnname+'已成功添加到数据库')
    },
    error: function () {
      //alert('数据添加出错')
    },
    complete: function () {
      //alert(vulnname+'已成功添加到数据库')
    }
  })


  $.getJSON("/showvulntitleinterfaceajax/",
    function (info) {
      document.getElementById("titlespanid").innerHTML = info.indexadddatastatus;
      //alert(info.indexadddatastatus)
    })
}


//ajax异步清空es数据库
function clearesfunc() {
  $.ajax({
    url: '/clearelasticsearch/',
    method: 'GET',
    success: function (res) {
      console.log(res)
      console.log('ES库清空成功')
    },
    error: function () {
      alert('ES库未开启')
    },
    complete: function () {
      alert('ES库清空完成')
    }
  })
}


//ajax异步添加ES数据库
function addesfunc() {
  $.ajax({
    url: '/addelasticsearch/',
    method: 'GET',
    success: function (res) {
      console.log(res)
      console.log('ES库添加成功')
    },
    error: function () {
      alert('ES库未开启')
    },
    complete: function () {
      alert('ES库添加完成')
    }
  })
}


//通过ID查询数据
function selectbyidfunc(value) {

  document.getElementById('div').style.display = "block";
  $.ajax({
    url: '/selectbyid?id=' + value,
    method: 'GET',
    success: function (res) {
      console.log(res)
    },
    error: function () {
    },
    complete: function () {
    }
  })
  $.getJSON("/selectbyidajax/",
    function (info) {
      document.getElementById("vulnname").value = info.valnname11;
      document.getElementById("ip").value = info.ip11;
      document.getElementById("id").value = info.id11;
    })
}


//ip异步方式反查漏洞标题
function selectvulnnamebyipfunc() {
  var ipbyajax = $('input[name="ipbyajax"]').val();
  $.ajax({
    url: '/selectvulnnamebyip/?ip=' + ipbyajax,
    method: 'GET',
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {
    }
  })
  $.getJSON("/selectvulnnamebyipajax/",
    function (info) {
      $('#opbyid').empty();
      for (var i = 0; i < info.vuln_name.length; i++) {
        $('#opbyid').append('<option>' + info.vuln_name[i] + '</option><br>');
      }
    })
}



//ajax异步通过时间段查询漏洞标题和时间
function selectvulntimebyajaxfunc() {
  var obj = document.getElementById("class_id"); //定位id
  var index = obj.selectedIndex; // 选中索引
  var text = obj.options[index].text; // 选中文本
  var oper = obj.options[index].value; // 选中值

  $.ajax({
    url: '/selectallbycycle/',
    method: 'POST',
    data: {
      oper: oper
    },
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {

    }
  })


  $.getJSON("/selectvulntimebyajax/",
    function (info) {
      $('#optionbyid1').empty();
      for (var i = 0; i < info.vuln_time_list_result.length; i++) {
        $('#optionbyid1').append('<option>' + info.vuln_time_list_result[i] + '</option><br>');
      }
    })


  $.getJSON("/selectvulntimebyajax/",
    function (info) {
      $('#optionbyid2').empty();
      for (var i = 0; i < info.date_time_list_result.length; i++) {
        $('#optionbyid2').append('<option>' + info.date_time_list_result[i] + '</option><br>');
      }
    })

  $.getJSON("/selectvulntimebyajax/",
    function (info) {
      $('#optionbyid3').empty();
      document.getElementById("optionbyid3").innerHTML = info.vuln_count_list_result;
    })

}



//漏洞标题异步反查IP
function selectipbyvulnnamefunc() {
  //var opidname = $('option[name="opid"]').val();
  var obj = document.getElementById('opbyid3'); //定位id
  var index = obj.selectedIndex; // 选中索引
  var text = obj.options[index].text; // 选中文本
  var value = obj.options[index].value; // 选中值

  $.ajax({
    url: '/selectipbyvulnname/?ip=' + value,
    method: 'GET',
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {

    }
  })
  $.getJSON("/selectipbyvulnnameajax/",
    function (info) {
      $('#opbyid3').empty();
      for (var i = 0; i < info.ip_name.length; i++) {
        $('#opbyid3').append('<option>' + info.ip_name[i] + '</option><br>');
      }
    })
}


//隐藏
function hidd() {
  document.getElementById('div').style.display = "none";
}





//异步通过关键字查询漏洞标题称
function vulnnamekeyajaxfunc() {
  var vulnnamekeyajax = $('input[name="vulnnamekeyajax"]').val();
  $.ajax({
    url: '/selectvulnnamebykey/',
    method: 'POST',
    data: {
      vulnnamekeyajax: vulnnamekeyajax
    },
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {

    }
  })

  $.getJSON("/selectvulnnamebykeyajax/",
    function (info) {
      $('#opbyid2').empty();
      for (var i = 0; i < info.vuln_name_key.length; i++) {
        $('#opbyid2').append('<option>' + info.vuln_name_key[i] + '</option><br>');
      }
    })

  $.getJSON("/selectvulnconutbyajax/",
    function (info) {
      $('#conutid').empty();
      document.getElementById("conutid").innerHTML = info.vulncount;
    })
  //异步查询IP地址
  $.ajax({
    url: '/selectipbykey/',
    method: 'POST',
    data: {
      vulnnamekeyajax: vulnnamekeyajax
    },
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {

    }
  })

  $.getJSON("/selectvulnnamebykeyajax/",
    function (info) {
      $('#opbyid5').empty();
      for (var i = 0; i < info.ip_name_key.length; i++) {
        $('#opbyid5').append('<option>' + info.ip_name_key[i] + '</option><br>');
      }
    })


  //异步查询数据录入时间
  $.ajax({
    url: '/selectdatenowbykey/',
    method: 'POST',
    data: {
      vulnnamekeyajax: vulnnamekeyajax
    },
    success: function (res) {
      console.log(res)
    },
    error: function () {

    },
    complete: function () {

    }
  })

  $.getJSON("/selectvulnnamebykeyajax/",
    function (info) {
      $('#opbyid6').empty();
      for (var i = 0; i < info.date_now_name_key.length; i++) {
        $('#opbyid6').append('<option>' + info.date_now_name_key[i] + '</option><br>');
      }
    })
}




function stopvulnfunc() {
  document.getElementById('div1').style.display = "none";
}



function startvulnfunc() {
  document.getElementById('div1').style.display = "block";
}




//ajax异步修改数据
function updatevulnfunc() {
  var vulnnames = $('input[name="vulnnames"]').val();
  var ips = $('input[name="ips"]').val();
  var ids = $('input[name="ids"]').val();

  $.ajax({
    url: '/updatebyid/',
    method: 'POST',
    data: {
      vulnnames: vulnnames,
      ips: ips,
      ids: ids
    },
    success: function (res) {
      console.log(res)
      console.log('修改成功')
    },
    error: function () {
      alert('修改失败')
    },
    complete: function () {
      alert('修改成功')
    }
  })
}



//ajax异步方式添加漏洞网址到数据库中
function addvulnurlfunc() {
  var vulnurl = $('input[name="vulnurl"]').val();

  $.ajax({
    url: '/addvulnurlinterface/',
    method: 'POST',
    data: {
      vulnurl: vulnurl
    },
    success: function (res) {
      console.log(res)

    },
    error: function () {

    },
    complete: function () {

    }
  })

  $.getJSON("/showvulnurlinterfaceajax/",
    function (info) {
      document.getElementById("urlspanid").innerHTML = info.vuln_url_message;
    })
}