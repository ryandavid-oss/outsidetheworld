<?php

$include_path = dirname(__FILE__);
if ($include_path == "/") {
    $include_path = ".";
}

if (!isset($PHP_SELF)) {
    global $HTTP_GET_VARS, $HTTP_POST_VARS, $HTTP_SERVER_VARS;
    $PHP_SELF = $HTTP_SERVER_VARS["PHP_SELF"];
    if (isset($HTTP_GET_VARS)) {
        while (list($name, $value)=each($HTTP_GET_VARS)) {
            $$name=$value;
        }
    }
    if (isset($HTTP_POST_VARS)) {
        while (list($name, $value)=each($HTTP_POST_VARS)) {
            $$name=$value;
        }
    }
    if(isset($HTTP_COOKIE_VARS)){
        while (list($name, $value)=each($HTTP_COOKIE_VARS)){
            $$name=$value;
        }
    }
}

require $include_path."/include/config.inc.php";
require $include_path."/include/class_poll.php";

$php_poll = new poll();
$php_poll->set_include_path($include_path);

?>