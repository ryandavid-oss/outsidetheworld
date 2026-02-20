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
<title>Demo 4</title>
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
    <td class="code" valign="top" align="left"> <font color="#003366"><font color="#666666">&lt;?php</font><font color="#003366"> 
      </font><font color="#003366"><font color="#0000FF"><br>
      <font color="#009999">/* Include this before your html code */</font><br>
      include</font> &quot;./poll_cookie.php&quot;</font>;<font color="#003366"> 
      <font color="#666666"><br>
      ?&gt;<br>
      </font></font> </font>
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
      <font color="#009999">/* question */</font><br>
      <font color="#0000FF">echo</font> $php_poll-&gt;get_poll_question(<font color="#FF0000">2</font>);<br>
      <br>
      <br>
      <font color="#009999">/* poll */</font><br>
      $php_poll-&gt;set_template_set(<font color="#003366">&quot;plain&quot;</font>);<br>
      $php_poll-&gt;set_max_bar_length(<font color="#FF0000">125</font>);<br>
      $php_poll-&gt;set_max_bar_height(<font color="#FF0000">10</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;poll_process(<font color="#FF0000">2</font>);<br>
      <br>
      <br>
      <font color="#009999">/* construct the form */</font><br>
      $php_poll-&gt;set_template(<font color="#003366">&quot;poll_form&quot;</font>);<br>
      $php_poll-&gt;set_form_error(<font color="#0000FF">array</font>(<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&quot;name&quot; =&gt; <font color="#003366">&quot;Please 
      enter your name.&quot;</font>,<br>
      <font color="#009999"> //&nbsp;&quot;email&quot; =&gt; &quot;You must specify 
      your e-mail address.&quot;,</font><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot; =&gt; <font color="#003366">&quot;You 
      must specify a message.&quot;</font><br>
      ));<br>
      $html_form = $php_poll-&gt;comment_process(<font color="#FF0000">2</font>);<br>
      <br>
      <br>
      <font color="#009999">/* poll comments */</font><br>
      $php_poll-&gt;set_template(<font color="#003366">&quot;poll_comment&quot;</font>);<br>
      $php_poll-&gt;set_comments_per_page(<font color="#FF0000">5</font>);<br>
      $php_poll-&gt;set_date_format(<font color="#003366">&quot;d/m/Y H:i&quot;</font>);<br>
      $php_poll-&gt;data_order_by(<font color="#003366">&quot;time&quot;,&quot;desc&quot;</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;view_poll_comments(<font color="#FF0000">2</font>);<br>
      <font color="#0000FF">echo</font> $php_poll-&gt;get_comment_pages(<font color="#FF0000">2</font>); 
      <br>
      <br>
      <font color="#009999">/* form */</font><br>
      <font color="#0000FF">echo</font> $html_form;<br>
      <br>
      ?<font color="#003366"><font color="#003366"><font color="#666666">&gt;<br>
      </font></font></font></td>
    <td width="10" align="center">&nbsp;</td>
    <td width="2" bgcolor="#999999" align="center">&nbsp;</td>
    <td width="20" align="center" valign="top">&nbsp;</td>
    <td valign="top"> 
      <?php
/* path */
require $poll_path."/include/config.inc.php";
require $poll_path."/include/class_poll.php";
require $poll_path."/include/class_pollcomment.php";

$php_poll = new pollcomment();

/* question */
echo "<h4>".$php_poll->get_poll_question(2)."</h4>";

/* poll */
$php_poll->set_template_set("plain");
$php_poll->set_max_bar_length(125);
$php_poll->set_max_bar_height(10);
echo $php_poll->poll_process(2);

/* construct the form */
$php_poll->set_template("poll_form");
$php_poll->set_form_error(array(
    "name"    => "Please enter your name.",
 // "email"   => "You must specify your e-mail address.",
    "message" => "You must specify a message."
));
$html_form = $php_poll->comment_process(2);

/* poll comments */
$php_poll->set_template("poll_comment");
$php_poll->set_comments_per_page(5);
$php_poll->set_date_format("d/m/Y H:i");
$php_poll->data_order_by("time","desc");
echo $php_poll->view_poll_comments(2);
echo "<center><font size=1 face=Verdana>".$php_poll->get_comment_pages(2)."</font></center>";

/* form */
echo $html_form;

?>
    </td>
    <td align="center" valign="top">&nbsp; </td>
  </tr>
</table>
</body>
</html>
