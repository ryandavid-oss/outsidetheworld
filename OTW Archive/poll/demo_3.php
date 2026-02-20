<?php
$poll_path = dirname(__FILE__);
if (eregi("WIN",PHP_OS)) {
    $poll_path = str_replace("\\","/",$poll_path);
}
require ("./poll_cookie.php");
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . "GMT");
header("Cache-Control: no-cache, must-revalidate");
header("Pragma: no-cache");
?>
<html>
<head>
<title>Demo 3</title>
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
      include</font> &quot;./poll_cookie.php&quot;</font>;<font color="#003366"> 
      <font color="#666666"><br>
      ?&gt;<br>
      </font></font> 
      <hr size="1">
      <font color="#003366"><font color="#666666">&lt;?php<br>
      <br>
      </font></font> <font color="#009999">/* path */</font><br>
      $poll_path = <font color="#003366">&quot;<?php echo $poll_path; ?>&quot;</font>;<font color="#009900"><br>
      </font><br>
      <font color="#0000FF">require</font> $poll_path.<font color="#003366">&quot;/include/config.inc.php&quot;</font>;<br>
      <font color="#0000FF">require</font> $poll_path.<font color="#003366">&quot;/include/class_poll.php&quot;</font>;<br>
      <font color="#0000FF">require</font> $poll_path.<font color="#003366">&quot;/include/class_pollcomment.php&quot;</font>;<br>
      <font color="#0000FF">require</font> $poll_path.<font color="#003366">&quot;/include/class_plist.php&quot;</font>;<br>
      <br>
      $php_poll = new plist();<br>
      <br>
      <font color="#009999">/* poll */</font><br>
      $php_poll-&gt;set_template_set(<font color="#003366">&quot;plain&quot;</font>);<br>
      $php_poll-&gt;set_max_bar_length(<font color="#FF0000">125</font>);<br>
      $php_poll-&gt;set_max_bar_height(<font color="#FF0000">10</font>);<br>
      <font color="#009900">if</font> (<font color="#0000FF">isset</font>($<font color="#990000">HTTP_GET_VARS</font>['poll_id'])) 
      {<br>
      &nbsp;&nbsp;&nbsp;<font color="#0000FF">echo</font> $php_poll-&gt;poll_process($<font color="#990000">HTTP_GET_VARS</font>['poll_id']);<br>
      } <font color="#009900">else</font> {<br>
      &nbsp;&nbsp;&nbsp;<font color="#0000FF">echo</font> $php_poll-&gt;poll_process(<font color="#003366">&quot;random&quot;</font>);<br>
      }<br>
      <br>
      <font color="#009999">/* poll list */</font><br>
      $php_poll-&gt;set_template(<font color="#003366">&quot;poll_list&quot;</font>);<br>
      $php_poll-&gt;set_date_format(<font color="#003366">&quot;m/d/Y&quot;</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;view_poll_list();<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;get_list_pages();<br>
      <br>
      ?<font color="#003366"><font color="#003366"><font color="#666666">&gt;<br>
      </font></font></font></td>
    <td width="10" align="center">&nbsp;</td>
    <td width="2" bgcolor="#999999" align="center">&nbsp;</td>
    <td width="20" align="center">&nbsp;</td>
    <td align="center" valign="top"> 

<?php
$poll_path = dirname(__FILE__);
require $poll_path."/include/config.inc.php";
require $poll_path."/include/class_poll.php";
require $poll_path."/include/class_pollcomment.php";
require $poll_path."/include/class_plist.php";

$php_poll = new plist();

/* poll */
$php_poll->set_template_set("plain");
$php_poll->set_max_bar_length(125);
$php_poll->set_max_bar_height(10);
if (isset($HTTP_GET_VARS['poll_id'])) {
    echo $php_poll->poll_process($HTTP_GET_VARS['poll_id']);
} else {
    echo $php_poll->poll_process("random");
}

/* poll list */
$php_poll->set_template("poll_list");
$php_poll->set_date_format("m/d/Y");
echo $php_poll->view_poll_list();
echo $php_poll->get_list_pages();

?>

    </td>
  </tr>
</table>
</body>
</html>
