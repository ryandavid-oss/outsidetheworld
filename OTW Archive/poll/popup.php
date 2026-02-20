<?php
include "./poll_cookie.php";
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . "GMT");
header("Cache-Control: no-cache, must-revalidate");
header("Pragma: no-cache");
include "./booth.php";
?>
<html>
<head>
<title><?php echo $php_poll->pollvars["title"]; ?></title>
</head>
<body bgcolor="#FFFFFF">
<br>
<center>
<?php
$php_poll->set_template_set("popup");
if (isset($poll_ident) && isset($action)) {
    $php_poll->set_max_bar_length(110);
    echo $php_poll->poll_process($poll_ident);
}
?>
</center>
</body>
</html>
