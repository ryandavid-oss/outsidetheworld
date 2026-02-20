<?php
require "./poll_cookie.php";
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . "GMT");
header("Cache-Control: no-cache, must-revalidate");
header("Pragma: no-cache");

include "./booth.php";

if (isset($HTTP_SERVER_VARS['QUERY_STRING_UNESCAPED'])) {
    list($uri,$ssi_vars) = explode("?",$HTTP_SERVER_VARS['REQUEST_URI']);
    $ssi_vars = explode("&",$ssi_vars);
    for ($i=0; $i<sizeof($ssi_vars); $i++) {
        list($name, $value) = explode("=",$ssi_vars[$i]);
        $$name=$value;
    }
}

if (isset($tpl_set)) {
    $php_poll->set_template_set("$tpl_set");    
}

$RANDOM_POLL = (isset($poll_id) && ($poll_id == "random")) ? true : false;

if (!isset($action)) {
    $action='';
} elseif ($action=="vote") {
    $poll_id = $poll_ident;
}
if (!isset($poll_ident)) {
    $poll_ident='';
}

if ($RANDOM_POLL) {
    if (isset($random)) {
        $poll_id = $random;
    } elseif (!empty($poll_ident)) {    
        $poll_id = $poll_ident;
    } else {
        $poll_id = $php_poll->get_random_poll_id();
    }
} elseif ($poll_id=="newest") {
    $poll_id = $php_poll->get_latest_poll_id();
}
if ($php_poll->is_valid_poll_id($poll_id)) {
    $voted = $php_poll->has_voted($poll_id);
    $is_active = $php_poll->is_active_poll_id($poll_id);
    switch ($action) {

        case "vote":
            $poll_type = (isset($random)) ? "random" : "poll_ident";
            if (!$voted && isset($option_id)) {
                $php_poll->update_poll($poll_id,$option_id);                
                header("Location: ".$poll_ref."?$poll_type=$poll_id");
                exit();
            } else {
                header("Location: ".$poll_ref."?$poll_type=$poll_id");
                exit();
            }

        case "results":
            if (($poll_ident == $poll_id) && isset($HTTP_SERVER_VARS['QUERY_STRING_UNESCAPED'])) {       
                echo $php_poll->view_poll_result($poll_id,0);
                break;
            }           
    
        default:
            if (!$is_active) {       
                echo $php_poll->view_poll_result($poll_id,0);
            } elseif ($is_active && $voted) {
                echo $php_poll->view_poll_result($poll_id,1);      
            } else {                
                $php_poll->form_forward = $HTTP_SERVER_VARS['DOCUMENT_URI'];
                $poll_html = $php_poll->display_poll($poll_id);
                $poll_html = eregi_replace("action=\"$HTTP_SERVER_VARS[DOCUMENT_URI]\"", "action=\"$PHP_SELF?poll_ref=$HTTP_SERVER_VARS[DOCUMENT_URI]\"", "$poll_html");
                echo "$poll_html";
            }
    }
} else {
    echo "<b>Poll ID <font color=red>$poll_id</font> does not exist.</b>";
}

?>