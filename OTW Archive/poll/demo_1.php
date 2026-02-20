<?php
$poll_path = dirname(__FILE__);
if (eregi("WIN",PHP_OS)) {
    $poll_path = str_replace("\\","/",$poll_path);
}
require "./poll_cookie.php";
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . "GMT");
header("Cache-Control: no-cache, must-revalidate");
header("Pragma: no-cache");
?>
<html>
<head>
<title>Demo 1</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type="text/css">
<!--
.code {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px}
-->
</style>
</head>
<body bgcolor="#FFFFFF" text="#000000">
<table border="0" cellspacing="0" cellpadding="4" width="400">
  <tr> 
    <td> <font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_1.php" target="_self">Demo 
      1</a></font></td>
    <td><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_2.php" target="_self">Demo 
      2</a></font></td>
    <td><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_3.php" target="_self">Demo 
      3</a></font></td>
    <td><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_4.php" target="_self">Demo 
      4</a></font></td>
    <td><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_5.shtml" target="_self">Demo 
      5</a></font></td>
    <td><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a href="demo_6.php" target="_self">Demo 
      6</a></font></td>
  </tr>
</table>
<hr>
<br>
<table cellpadding="0" cellspacing="0">
  <tr> 
    <td class="code" valign="top" align="left"><font color="#666666">&lt;?php</font><font color="#003366"> 
      </font><font color="#003366"><font color="#0000FF"><br>
      <font color="#009999">/* Include this before your html code */</font><br>
      include</font> &quot;./poll_cookie.php&quot;</font>;<font color="#666666"> 
      <br>
      ?&gt;<br>
      </font> 
      <hr size="1">
      <font color="#666666">&lt;?php<br>
      <br>
      </font><font color="#009999">/* path */</font><font color="#666666"> </font><font color="#0000FF"><br>
      </font>$poll_path = <font color="#003366">&quot;<?php echo $poll_path; ?>&quot;</font>;<font color="#009900"><br>
      </font><font color="#0000FF"><br>
      require </font>$poll_path.<font color="#0000FF"><font color="#003366">&quot;/include/config.inc.php&quot;</font></font>;<font color="#0000FF"><br>
      require </font>$poll_path.<font color="#0000FF"><font color="#003366">&quot;/include/class_poll.php&quot;</font></font>; 
      <br>
      <br>
      $php_poll = new poll();<br>
      <br>
      <font color="#009999">/* the first poll */</font> <br>
      <font color="#003366"><font color="#0000FF">echo</font> <font color="#000000">$</font></font>php_poll-&gt;poll_process(<font color="#FF0000">1</font>);<br>
      <br>
      <br>
      <font color="#009999">/* the second poll */</font><br>
      $php_poll-&gt;set_template_set(<font color="#003366">&quot;simple&quot;</font>);<font color="#003366"><br>
      </font>$php_poll-&gt;set_max_bar_length(<font color="#FF0000">80</font>);<font color="#003366"> 
      <br>
      <font color="#0000FF">echo</font> </font>$php_poll-&gt;poll_process(<font color="#FF0000">2</font>);<br>
      <br>
      <font color="#009999"><br>
      /* the third poll */</font><br>
      $php_poll-&gt;set_template_set(<font color="#003366">&quot;popup&quot;</font>);<font color="#003366"><br>
      <font color="#009900">if</font> <font color="#009900">(</font><font color="#000000">$</font></font>php_poll-&gt;is_valid_poll_id(<font color="#FF0000">3</font>))<font color="#003366"> 
      </font>{<font color="#003366"><br>
      <font color="#0000FF">&nbsp;&nbsp;&nbsp;&nbsp;echo</font> </font>$php_poll-&gt;display_poll(<font color="#FF0000">3</font>);<font color="#003366"><br>
      <font color="#000000">}</font> </font><br>
      <br>
      ?<font color="#666666">&gt;<br>
      </font></td>
    <td width="10" align="center">&nbsp;</td>
    <td width="2" bgcolor="#999999" align="center">&nbsp;</td>
    <td width="20" align="center" valign="top"> 
      <table border="0" cellspacing="0" cellpadding="3" width="640">
        <tr> 
          <td valign="top" align="center"> 
<?php
require $poll_path."/include/config.inc.php";
require $poll_path."/include/class_poll.php";

$php_poll = new poll();

/* the first poll */ 
echo $php_poll->poll_process(1);
?>
          </td>
          <td valign="top" align="center"> 
<?php
/* the second poll */ 
$php_poll->set_template_set("simple");
$php_poll->set_max_bar_length(80);
echo $php_poll->poll_process(2);
?>
          </td>
          <td valign="top" align="center"> 
<?php
/* the third poll */ 
$php_poll->set_template_set("popup");
if ($php_poll->is_valid_poll_id(3)) {
    echo $php_poll->display_poll(3);
}
?>
          </td>
        </tr>
      </table>
    </td>
    <td align="center" valign="top">&nbsp; </td>
  </tr>
</table>
</body>
</html>
