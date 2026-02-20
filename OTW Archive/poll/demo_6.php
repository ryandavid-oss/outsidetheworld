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
<title>Demo 2</title>
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
      <br>
      $php_poll = new pollcomment();<br>
      <br>
      <font color="#009999">/* poll */</font><br>
      $php_poll-&gt;set_template_set(<font color="#003366">&quot;graphic&quot;</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;view_poll_result(<font color="#FF0000">1</font>);<br>
      <br>
      <br>
      <font color="#009999">/* poll comments */</font><br>
      $php_poll-&gt;set_template(<font color="#003366">&quot;poll_comment&quot;</font>);<br>
      $php_poll-&gt;set_comments_per_page(<font color="#FF0000">3</font>);<br>
      $php_poll-&gt;set_date_format(<font color="#003366">&quot;d/m/Y H:i&quot;</font>);<br>
      $php_poll-&gt;data_order_by(<font color="#003366">&quot;time&quot;,&quot;desc&quot;</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;view_poll_comments(<font color="#FF0000">1</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;get_comment_pages(<font color="#FF0000">1</font>); 
      <br>
      <br>
      ?<font color="#003366"><font color="#003366"><font color="#666666">&gt;<br>
      </font></font></font></td>
    <td width="10" align="center">&nbsp;</td>
    <td width="2" bgcolor="#999999" align="center">&nbsp;</td>
    <td width="20" align="center" valign="top">&nbsp;</td>
    <td align="center" valign="top"> 
      <?php
/* path */
$poll_path = dirname(__FILE__);
require $poll_path."/include/config.inc.php";
require $poll_path."/include/class_poll.php";
require $poll_path."/include/class_pollcomment.php";

$php_poll = new pollcomment();

/* poll */
$php_poll->set_template_set("graphic");
echo $php_poll->view_poll_result(1);

/* poll comments */
$php_poll->set_template("poll_comment");
$php_poll->set_comments_per_page(3);
$php_poll->set_date_format("d/m/Y H:i");
$php_poll->data_order_by("time","desc");
echo $php_poll->view_poll_comments(1);
echo "<font size=1 face=Verdana>".$php_poll->get_comment_pages(1)."</font>";

?>
    </td>
    <td align="center" valign="top">&nbsp; </td>
  </tr>
</table>
</body>
</html>
